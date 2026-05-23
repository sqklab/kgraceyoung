#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';

function parseEnvFile(path) {
  const env = {};
  if (!existsSync(path)) return env;
  const lines = readFileSync(path, 'utf8').split(/\r?\n/);
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    const idx = line.indexOf('=');
    if (idx === -1) continue;
    const key = line.slice(0, idx).trim();
    let value = line.slice(idx + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    env[key] = value;
  }
  return env;
}

function findRepoEnv(startDir) {
  let current = resolve(startDir);
  for (let i = 0; i < 8; i += 1) {
    const candidate = join(current, '.env');
    if (existsSync(candidate)) return candidate;
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return null;
}

const [command, ...args] = process.argv.slice(2);
if (!command) {
  console.error('Usage: node scripts/run-with-root-env.mjs <command> [...args]');
  process.exit(1);
}

const envPath = findRepoEnv(process.cwd());
const rootEnv = envPath ? parseEnvFile(envPath) : {};
const env = { ...rootEnv, ...process.env };

// Frontend convention: derive NEXT_PUBLIC_API_URL from API_ORIGIN when not explicitly set.
if (!env.NEXT_PUBLIC_API_URL && env.API_ORIGIN) env.NEXT_PUBLIC_API_URL = env.API_ORIGIN;
if (!env.NEXT_PUBLIC_CLIENT_ORIGIN && env.CLIENT_ORIGIN) env.NEXT_PUBLIC_CLIENT_ORIGIN = env.CLIENT_ORIGIN;
if (!env.NEXT_PUBLIC_ADMIN_ORIGIN && env.ADMIN_ORIGIN) env.NEXT_PUBLIC_ADMIN_ORIGIN = env.ADMIN_ORIGIN;
if (!env.NEXT_PUBLIC_DEFAULT_LOCALE && env.DEFAULT_LOCALE) env.NEXT_PUBLIC_DEFAULT_LOCALE = env.DEFAULT_LOCALE;
if (!env.NEXT_PUBLIC_SUPPORTED_LOCALES && env.SUPPORTED_LOCALES) env.NEXT_PUBLIC_SUPPORTED_LOCALES = env.SUPPORTED_LOCALES;
if (!env.NEXT_PUBLIC_DEFAULT_CURRENCY && env.DEFAULT_CURRENCY) env.NEXT_PUBLIC_DEFAULT_CURRENCY = env.DEFAULT_CURRENCY;

const child = spawn(command, args, { stdio: 'inherit', shell: process.platform === 'win32', env });
child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  process.exit(code ?? 0);
});
