/* AQUI A GENTE FAZ: cria a instância do Express

configura middlewares

define rotas OK

importa controllers

configura CORS

configura body-parser

trata erros

faz conexão com serviços (ex: Supabase)
*/

/* ROTAS DE PÁGINAS ESTÁTICAS */

const express = require('express');
const path = require('path');
const app = express();
const bodyParser = require('body-parser');

app.use(express.static(path.join(__dirname, '../../frontend/public')));

app.get("/", function(req, res) {
   res.sendFile(path.join(__dirname, '../../frontend/public/index.html'));
});

app.get("/colaborador", function(req, res) {
    res.sendFile(path.join(__dirname, '../../frontend/public/colaborador.html'));
});

app.get("/ct", function(req, res) {
    res.sendFile(path.join(__dirname, '../../frontend/public/ct.html'));
});

app.get("/contatos", function(req, res) {
    res.sendFile(path.join(__dirname, '../../frontend/public/contatos.html'));
});

app.get("/sobre", function(req, res) {
    res.sendFile(path.join(__dirname, '../../frontend/public/sobre.html'));
});

app.get("/proprietarios", function(req, res) {
    res.sendFile(path.join(__dirname, '../../frontend/public/proprietarios.html'));
});

// Rota para os formulários

const formMap = {
    //CANDIDATOS
    'arrumadeira': 'colab-forms/form-candi-arrumadeira.html',
    'baba': 'colab-forms/form-candi-baba.html',
    'casal': 'colab-forms/form-candi-casal.html',
    'caseiro': 'colab-forms/form-candi-caseiro.html',
    'copeiro': 'colab-forms/form-candi-copeiro.html',
    'cozinheira': 'colab-forms/form-candi-cozinheira.html',
    'governanta': 'colab-forms/form-candi-governanta.html',
    //VAGAS
    'vaga-arrumadeira' : 'vaga-forms/form-prop-arrumadeira.html',
    'vaga-baba' : 'vaga-forms/form-prop-baba.html',
    'vaga-casal' : 'vaga-forms/form-prop-casal.html',
    'vaga-caseiro' : 'vaga-forms/form-prop-caseiro.html',
    'vaga-copeiro' : 'vaga-forms/form-prop-copeiro.html',
    'vaga-cozinheira' : 'vaga-forms/form-prop-cozinheira.html',
    'vaga-governanta' : 'vaga-forms/form-prop-governanta.html'
};

// Roteamento para formulario de candidatos

app.get("/form/candidato/:tipo", function(req, res) {

    const tipo = req.params.tipo;
    const relativePath = formMap[tipo];

    if (!relativePath) {
        return res.status(404).send('Formulário não encontrado');
    }

    res.sendFile(path.join(__dirname, `../../frontend/public/forms/${relativePath}`));
});

// Roteamento para formulários de vagas

app.get("/form/vaga/:tipo", function(req, res) {

    const tipo = req.params.tipo;
    const relativePath = formMap[tipo];

    if (!relativePath) {
        return res.status(404).send('Formulário não encontrado');
    }

    res.sendFile(path.join(__dirname, `../../frontend/public/forms/${relativePath}`));
});

// ROTDAS DE POST DA API

const candidatosRoutes = require('../routes/candidatos.route');

app.use('/api/candidatos', candidatosRoutes);

//escutando a porta 8081
app.listen(8081, function() {
    console.log('Servidor rodando na porta 8081');
})