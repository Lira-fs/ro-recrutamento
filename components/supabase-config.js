/* ===================================
   R.O RECRUTAMENTO - SUPABASE CONFIG
   =================================== */

const SUPABASE_CONFIG = {
    url: 'https://vzhthegwwittuinvlfkg.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ6aHRoZWd3d2l0dHVpbnZsZmtnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ5MzM3MDksImV4cCI6MjA3MDUwOTcwOX0.vOk5rMEgK-W0FRp2ihYIUH22UTPm-Xrg8wxd7sIbyko'
};

// 📦 Cliente Supabase
import { createClient } from 'https://cdn.skypack.dev/@supabase/supabase-js@2';
const supabase = createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);

// Exportar para uso global
window.supabase = supabase;
window.SUPABASE_CONFIG = SUPABASE_CONFIG;
