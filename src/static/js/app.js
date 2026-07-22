/* ============================================================
   VendeMais — helpers compartilhados do painel
   ============================================================ */

const API_BASE = '/api';

/** Recupera o token salvo no login (usado nas chamadas fetch via header) */
function getToken() {
    return localStorage.getItem('vendemais_token');
}

function setToken(token) {
    localStorage.setItem('vendemais_token', token);
}

function clearToken() {
    localStorage.removeItem('vendemais_token');
}

/** Cabeçalhos padrão para chamadas autenticadas à API */
function authHeaders() {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

/** Exibe uma notificação temporária no canto da tela */
function showAlert(mensagem, tipo = 'info', duracaoMs = 3800) {
    let container = document.getElementById('alert-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'alert-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;
    toast.textContent = mensagem;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duracaoMs);
}

/** Garante que existe um token salvo localmente; caso contrário, manda para o login.
 *  Serve como segunda camada de proteção além do cookie/redirect do servidor. */
function requireAuth() {
    if (!getToken()) {
        window.location.href = '/auth/login';
    }
}

/** Faz logout: limpa token local, invalida cookie no servidor e volta pro login */
async function logout() {
    try {
        await fetch(`${API_BASE.replace('/api', '')}/auth/logout`, {
            method: 'POST',
            headers: authHeaders()
        });
    } catch (e) {
        // segue o fluxo mesmo se a chamada falhar
    } finally {
        clearToken();
        window.location.href = '/auth/login';
    }
}

/** Wrapper de fetch que trata 401 (sessão expirada) de forma consistente */
async function apiFetch(caminho, opcoes = {}) {
    const resposta = await fetch(`${API_BASE}${caminho}`, {
        ...opcoes,
        headers: { ...authHeaders(), ...(opcoes.headers || {}) }
    });

    if (resposta.status === 401) {
        clearToken();
        window.location.href = '/auth/login';
        throw new Error('Sessão expirada');
    }

    return resposta;
}

function formatarMoeda(valor) {
    return (Number(valor) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarData(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('pt-BR');
}

function formatarDataHora(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return `${d.toLocaleDateString('pt-BR')} às ${d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
}

/** Alterna o menu lateral em telas pequenas */
function toggleSidebar() {
    document.querySelector('.sidebar')?.classList.toggle('open');
}

/** Debounce simples para campos de busca */
function debounce(fn, atrasoMs = 400) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), atrasoMs);
    };
}

document.addEventListener('DOMContentLoaded', () => {
    // Fecha a sidebar (mobile) ao clicar fora dela
    document.addEventListener('click', (evento) => {
        const sidebar = document.querySelector('.sidebar');
        const toggle = document.querySelector('.topbar-toggle');
        if (!sidebar || !sidebar.classList.contains('open')) return;
        if (sidebar.contains(evento.target) || toggle?.contains(evento.target)) return;
        sidebar.classList.remove('open');
    });
});
