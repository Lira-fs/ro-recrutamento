const fs = require('fs');
const path = require('path');
const multer = require('multer');
const candidatosModel = require('../models/candidatos.model.js');
const { validateCandidate } = require('../validators/candidatos.validator.js');

const uploadDir = path.join(__dirname, '..', 'uploads', 'candidatos');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => {
    const safe = file.originalname.replace(/\s+/g, '_');
    cb(null, `${Date.now()}-${safe}`);
  }
});

const uploadAny = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 } // 5MB por arquivo
}).any();

function mapFiles(files = []) {
  return files.map(f => ({
    fieldname: f.fieldname,
    originalname: f.originalname,
    filename: f.filename,
    path: f.path,
    size: f.size,
    mimetype: f.mimetype
  }));
}

exports.uploadAny = uploadAny;

exports.createCaseiro = async (req, res) => {
  try {
    const body = req.body || {};
    const files = mapFiles(req.files || []);

    const payload = {
      ...body,
      files
    };

    // validação
    validateCandidate(payload);

    const inserted = await candidatosModel.createCaseiro(payload);
    return res.status(201).json({ message: 'Candidato caseiro recebido', data: inserted });
  } catch (err) {
    console.error(err);
    if (err && err.status) return res.status(err.status).json({ error: err.message || 'Erro' });
    return res.status(500).json({ error: 'Erro interno ao processar candidatura' });
  }
};

exports.createByTipo = async (req, res) => {
  try {
    const tipo = req.params.tipo || 'desconhecido';
    const body = req.body || {};
    const files = mapFiles(req.files || []);

    const payload = {
      ...body,
      files
    };

    // validação
    validateCandidate(payload);

    const inserted = await candidatosModel.createByTipo(tipo, payload);
    return res.status(201).json({ message: `Candidato tipo '${tipo}' recebido`, data: inserted });
  } catch (err) {
    console.error(err);
    if (err && err.status) return res.status(err.status).json({ error: err.message || 'Erro' });
    return res.status(500).json({ error: 'Erro interno ao processar candidatura' });
  }
};