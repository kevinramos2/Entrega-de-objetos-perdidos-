import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { AdminRoute, ProtectedRoute } from './components/ProtectedRoute'
import { PanelLayout } from './components/panel/PanelLayout'
import AuthCallback from './pages/AuthCallback'
import Home from './pages/Home'
import Login from './pages/Login'
import MisSolicitudes from './pages/MisSolicitudes'
import ObjetoDetalle from './pages/ObjetoDetalle'
import Objetos from './pages/Objetos'
import Categorias from './pages/panel/Categorias'
import ConfiguracionEntrega from './pages/panel/ConfiguracionEntrega'
import Dashboard from './pages/panel/Dashboard'
import ObjetoForm from './pages/panel/ObjetoForm'
import ObjetosAdmin from './pages/panel/ObjetosAdmin'
import SolicitudDetalle from './pages/panel/SolicitudDetalle'
import Solicitudes from './pages/panel/Solicitudes'
import UsuarioForm from './pages/panel/UsuarioForm'
import Usuarios from './pages/panel/Usuarios'
import StyleGuide from './pages/StyleGuide'

export default function App() {
  return (
    <Routes>
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/dev/styleguide" element={<StyleGuide />} />

      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/objetos" element={<Objetos />} />
          <Route path="/objetos/:id" element={<ObjetoDetalle />} />
          <Route path="/mis-solicitudes" element={<MisSolicitudes />} />
        </Route>
      </Route>

      <Route path="/panel" element={<AdminRoute />}>
        <Route element={<PanelLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="objetos" element={<ObjetosAdmin />} />
          <Route path="objetos/nuevo" element={<ObjetoForm />} />
          <Route path="objetos/:id/editar" element={<ObjetoForm />} />
          <Route path="solicitudes" element={<Solicitudes />} />
          <Route path="solicitudes/:id" element={<SolicitudDetalle />} />
          <Route path="categorias" element={<Categorias />} />
          <Route path="usuarios" element={<Usuarios />} />
          <Route path="usuarios/:id/editar" element={<UsuarioForm />} />
          <Route path="configuracion-entrega" element={<ConfiguracionEntrega />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
