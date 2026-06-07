'use client';
import { FormEvent, useEffect, useState } from 'react';
import AdminShell from '../AdminShell';
import { api } from '../lib';
export default function Settings(){const [json,setJson]=useState('');const [msg,setMsg]=useState('');useEffect(()=>{api('/admin/settings').then(j=>setJson(JSON.stringify(j.store||j,null,2))).catch(e=>setMsg(e.message))},[]);async function submit(e:FormEvent){e.preventDefault();await api('/admin/settings/store',{method:'PUT',body:JSON.stringify({value:JSON.parse(json)})});setMsg('Store settings saved')}return <AdminShell><header className="pageHead"><p>Settings</p><h1>Store Settings</h1><span>Store name, currency, locales, tax, provider and operational defaults.</span></header>{msg&&<div className="notice">{msg}</div>}<section className="panel"><form onSubmit={submit}><textarea className="jsonBox" value={json} onChange={e=>setJson(e.target.value)}/><button>Save Settings</button></form></section></AdminShell>}
