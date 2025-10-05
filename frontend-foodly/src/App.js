import logo from './logo.svg';
import './App.css';
import Foodlist from './components/Foodlist';
import Navbar from './Navbar/navbar';

function App() {
  return (
    <div className="App">
      <Navbar/>
      <Foodlist />
    </div>
  );
}

export default App;
