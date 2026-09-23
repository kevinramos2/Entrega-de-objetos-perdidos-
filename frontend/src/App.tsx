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
import Dashboard from './pages/panel/Dashboard'
import ObjetosAdmin from './pages/panel/ObjetosAdmin'
import PanelPlaceholder from './pages/PanelPlaceholder'
import StyleGuide from './pages/StyleGuide'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/dev/styleguide" element={<StyleGuide />} />

      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />

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
          <Route path="solicitudes" element={<PanelPlaceholder />} />
          <Route path="categorias" element={<PanelPlaceholder />} />
          <Route path="usuarios" element={<PanelPlaceholder />} />
          <Route path="configuracion-entrega" element={<PanelPlaceholder />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
