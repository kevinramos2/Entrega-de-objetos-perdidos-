import { Navigate, Route, Routes } from 'react-router-dom'
import { AdminRoute, ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'
import AuthCallback from './pages/AuthCallback'
import Home from './pages/Home'
import Login from './pages/Login'
import MisSolicitudes from './pages/MisSolicitudes'
import ObjetoDetalle from './pages/ObjetoDetalle'
import Objetos from './pages/Objetos'
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

        <Route element={<AdminRoute />}>
          <Route path="/panel" element={<PanelPlaceholder />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
