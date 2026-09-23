"""Autenticación de la API: login/refresh por cookie HttpOnly + puente para
el login con Google (que sigue siendo 100% Django/allauth por dentro)."""
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from ..views.helpers import (
    _clave_ip,
    _clave_login,
    intentos_bloqueados,
    limpiar_intentos,
    obtener_ip,
    registrar_intento_fallido,
)
from .serializers import UsuarioActualSerializer

COOKIE_PATH = '/api/v1/auth/'


def _set_refresh_cookie(response, token_str):
    max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME, token_str,
        max_age=max_age, httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )


def _respuesta_con_tokens(usuario, request):
    refresh = RefreshToken.for_user(usuario)
    datos = {
        'access': str(refresh.access_token),
        'usuario': UsuarioActualSerializer(usuario, context={'request': request}).data,
    }
    response = Response(datos, status=200)
    _set_refresh_cookie(response, str(refresh))
    return response


class LoginView(APIView):
    """Login local: acepta usuario o correo institucional, igual que la
    vista clásica ``iniciar_sesion``, con el mismo límite de intentos."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        identificador = (request.data.get('identificador') or '').strip()
        clave = request.data.get('contrasena') or ''
        if not identificador or not clave:
            return Response({'detail': 'Escribe tu usuario o correo y tu contraseña.'}, status=400)

        ip = obtener_ip(request)
        claves = [_clave_login(identificador), _clave_ip(ip)]
        if intentos_bloqueados(*claves):
            return Response(
                {'detail': 'Demasiados intentos fallidos. Espera unos minutos e inténtalo de nuevo.'},
                status=429,
            )

        usuario = authenticate(request, username=identificador, password=clave)
        if usuario is None and '@' in identificador:
            try:
                cuenta = User.objects.get(email__iexact=identificador)
                usuario = authenticate(request, username=cuenta.username, password=clave)
            except User.DoesNotExist:
                usuario = None

        if usuario is None or not usuario.is_active:
            registrar_intento_fallido(*claves)
            return Response({'detail': 'Usuario o contraseña incorrectos.'}, status=401)

        limpiar_intentos(*claves)
        return _respuesta_con_tokens(usuario, request)


class RefreshView(APIView):
    """Emite un access token nuevo a partir del refresh token en la cookie
    HttpOnly. El frontend la llama en silencio cuando un endpoint responde
    401, sin que el usuario note nada."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        token_str = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        if not token_str:
            return Response({'detail': 'Sesión expirada. Vuelve a iniciar sesión.'}, status=401)
        try:
            refresh = RefreshToken(token_str)
            access = str(refresh.access_token)
        except TokenError:
            return Response({'detail': 'Sesión expirada. Vuelve a iniciar sesión.'}, status=401)
        return Response({'access': access}, status=200)


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        response = Response(status=204)
        response.delete_cookie(settings.REFRESH_COOKIE_NAME, path=COOKIE_PATH)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UsuarioActualSerializer(request.user, context={'request': request}).data)


@login_required
def google_auth_bridge(request):
    """Destino final del login con Google (ver ``adapters.py``): en este
    punto allauth ya autenticó al usuario en la sesión de Django (validando
    el dominio institucional como siempre). Aquí solo se traduce esa sesión
    a un refresh token en cookie y se entrega el control a la SPA."""
    response = redirect(f'{settings.FRONTEND_URL}/auth/callback')
    refresh = RefreshToken.for_user(request.user)
    _set_refresh_cookie(response, str(refresh))
    return response
