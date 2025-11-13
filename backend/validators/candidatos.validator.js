/**
 * Validações simples para candidatos.
 * Exporta função validateCandidate(data) que lança um erro com shape { status, message }
 */
function validateCandidate(data = {}) {
	const errors = [];
	if (!data.nome || String(data.nome).trim().length === 0) {
		errors.push('Campo "nome" é obrigatório.');
	}

	// Exemplo: validar telefone ou email se necessário
	// if (!data.email) errors.push('Campo "email" é obrigatório.');

	if (errors.length) {
		const err = new Error(errors.join(' '));
		err.status = 400;
		throw err;
	}

	return true;
}

module.exports = {
	validateCandidate
};
