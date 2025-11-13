const supabase = require('./supabase');

async function testConnection() {
  console.log('🔄 Testando conexão com Supabase...');

  const { data, error } = await supabase.from('candidatos').select('id').limit(1);

  if (error) {
    console.error('❌ Erro ao conectar:', error);
  } else {
    console.log('✅ Conexão funcionando! Dados retornados:', data);
  }
}

testConnection();
