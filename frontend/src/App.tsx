import { Route, Routes } from 'react-router-dom'
import Placeholder from './pages/Placeholder'
import StyleGuide from './pages/StyleGuide'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Placeholder />} />
      <Route path="/dev/styleguide" element={<StyleGuide />} />
    </Routes>
  )
}
