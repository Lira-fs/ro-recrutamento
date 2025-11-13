const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const candidatosController = require('../controllers/candidatos.controller.js');

// rota específica mantida (pode ter lógica própria)
router.post('/caseiro', candidatosController.uploadAny, candidatosController.createCaseiro);

// Tenta registrar rotas dinâmicas com base nos arquivos de formulário em
// frontend/public/forms/colab-forms (nomes: form-candi-<tipo>.html)
try {
	const formsDir = path.resolve(__dirname, '..', '..', 'frontend', 'public', 'forms', 'colab-forms');
	const files = fs.readdirSync(formsDir);
	const tipos = Array.from(new Set(
		files
			.filter(f => /^form-candi-.*\.html$/i.test(f))
			.map(f => f.replace(/^form-candi-/i, '').replace(/\.html$/i, ''))
	));

	tipos.forEach(tipo => {
		// já temos rota /caseiro explicitamente
		if (!tipo || tipo.toLowerCase() === 'caseiro') return;
		router.post(`/${tipo}`, candidatosController.uploadAny, candidatosController.createByTipo);
	});
} catch (err) {
	// Não trava a inicialização do servidor caso a pasta não exista
	// (por exemplo em ambiente de produção separado). Logamos para depuração.
	// eslint-disable-next-line no-console
	console.warn('Rotas dinâmicas de candidatos não registradas:', err.message);
}

// rota genérica fallback (captura qualquer tipo não mapeado)
router.post('/:tipo', candidatosController.uploadAny, candidatosController.createByTipo);

module.exports = router;