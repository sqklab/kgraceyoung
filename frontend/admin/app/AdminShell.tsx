'use client';
import { useEffect, useState } from 'react';
const nav = [
  ['Dashboard','/'],['Orders','/orders'],['Products','/products'],['Inventory','/inventory'],['Customers','/customers'],['Banners','/banners'],['Reels','/reels'],['Coupons','/coupons'],['Shipping','/shipping'],['Payments','/payments'],['Reviews','/reviews'],['Settings','/settings']
];
export default function AdminShell({children}:{children:React.ReactNode}){
  const [email,setEmail]=useState('');
  useEffect(()=>{const t=localStorage.getItem('gy_admin_token'); const u=localStorage.getItem('gy_admin_user'); if(!t && location.pathname!='/login') location.href='/login'; if(u){try{setEmail(JSON.parse(u).email)}catch{}}},[]);
  function logout(){localStorage.removeItem('gy_admin_token');localStorage.removeItem('gy_admin_user');location.href='/login'}
  if (typeof window !== 'undefined' && location.pathname==='/login') return <>{children}</>;
  return <main className="adminShell"><aside className="sidebar"><div className="brand"><b>kgraceyoung</b><span>Back Office</span></div><nav>{nav.map(([label,href])=><a key={href} href={href}>{label}</a>)}</nav><div className="sideFoot"><span>{email||'admin'}</span><button onClick={logout}>Logout</button></div></aside><section className="workarea">{children}</section></main>
}
