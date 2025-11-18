import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { StationDetail } from './pages/StationDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <Link to="/" className="app-title">
            <h1>BC Fire Weather Dashboard</h1>
          </Link>
        </header>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/station/:id" element={<StationDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
