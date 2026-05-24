import { Outlet } from 'react-router-dom';
import Sidebar from '../Sidebar';


export default function MainLayout() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}