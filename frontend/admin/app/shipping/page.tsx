'use client';
import { FormEvent, useEffect, useState } from 'react';
import AdminShell from '../AdminShell';
import { api } from '../lib';
export default function Shipping(){const [json,setJson]=useState('');const [msg,setMsg]=useState('');useEffect(()=>{api('/admin/shipping/settings').then(j=>setJson(JSON.stringify(j,null,2))).catch(e=>setMsg(e.message))},[]);async function submit(e:FormEvent){e.preventDefault();await api('/admin/shipping/settings',{method:'PUT',body:JSON.stringify({value:JSON.parse(json)})});setMsg('Shipping settings saved')}return <AdminShell><header className="pageHead"><p>Shipping</p><h1>Rate & Fulfillment Settings</h1><span>Manage free shipping threshold, fixed rates, carriers and label behavior.</span></header>{msg&&<div className="notice">{msg}</div>}<section className="panel"><form onSubmit={submit}><textarea className="jsonBox" value={json} onChange={e=>setJson(e.target.value)}/><button>Save Settings</button></form></section></AdminShell>}
