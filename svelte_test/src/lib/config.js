// src/config.js
import { env } from '$env/dynamic/public';

export const ADDON_API_URL = env.PUBLIC_URL ?? "";
export const ADDON_REFRESH_INTERVAL = env.PUBLIC_INTERVAL ?? "";