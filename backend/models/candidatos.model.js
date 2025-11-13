const supabase = require('../core/db/supabase.js');

/**
 * Mapeia o "tipo" do formulário para a tabela correspondente no banco.
 * Adicione aqui novas entradas quando criar tabelas específicas.
 */
function getTableName(tipo) {
  const map = {
    caseiro: 'candidatos_caseiro',
    jardineiro: 'candidatos_jardineiro',
    cozinheiro: 'candidatos_cozinheiro',
    auxiliar: 'candidatos_auxiliar'
    // adicionar outros tipos conforme necessário
  };

  return map[tipo] || 'candidatos'; // tabela genérica como fallback
}

/**
 * Normaliza o payload antes de inserir.
 * - Garante que `nome` exista.
 * - Transforma metadata de arquivos em JSON (se houver).
 */
function normalizePayload(payload = {}) {
  const out = { ...payload };

//   if (!out.nome) {
//     throw { status: 400, message: 'Campo "nome" é obrigatório.' };
//   }

  // Se arquivos vierem como array de objetos, armazena como JSON (coluna files)
  if (Array.isArray(out.files)) {
    out.files = JSON.stringify(out.files);
  }

  // adicionar transformações/validações adicionais conforme necessidade
  return out;
}

module.exports = {
  createCaseiro: async (data) => {
    try {
      const payload = normalizePayload(data);
      const { data: inserted, error } = await supabase
        .from('candidatos_caseiro')
        .insert([payload])
        .select();

      if (error) throw error;
      return inserted;
    } catch (err) {
      throw err;
    }
  },

  /**
   * Insere candidato para um tipo dinâmico (caseiro, jardineiro, etc.)
   * Usa getTableName para decidir a tabela.
   * data: objeto contendo campos do formulário; pode incluir `files` (array de metadata).
   */
  createByTipo: async (tipo, data) => {
    try {
      const table = getTableName(tipo);
      const payload = normalizePayload(data);

      // opcional: armazena o tipo no registro
      payload.tipo = tipo;

      const { data: inserted, error } = await supabase
        .from(table)
        .insert([payload])
        .select();

      if (error) throw error;
      return inserted;
    } catch (err) {
      throw err;
    }
  }
};