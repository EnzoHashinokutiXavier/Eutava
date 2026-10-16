const botaoTema = document.getElementById('btn-tema');

function aplicarTema(tema) {
    document.documentElement.setAttribute('data-bs-theme', tema);
    localStorage.setItem('tema', tema);

    // Troca o ícone: lua no modo claro, sol no modo escuro
    if (botaoTema) {
        botaoTema.innerHTML = tema === 'dark' ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-fill"></i>';
    }
}

if (botaoTema) {
    // Mostra o ícone certo quando a página abre
    aplicarTema(document.documentElement.getAttribute('data-bs-theme'));

    botaoTema.addEventListener('click', () => {
        const temaAtual = document.documentElement.getAttribute('data-bs-theme');
        aplicarTema(temaAtual === 'dark' ? 'light' : 'dark');
    });
}
