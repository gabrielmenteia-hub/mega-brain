document.addEventListener('click', function(e) {
  if (e.target.matches('[data-clipboard]')) {
    navigator.clipboard.writeText(e.target.dataset.clipboard);
    e.target.textContent = 'Copiado!';
    setTimeout(() => e.target.textContent = 'Copiar para clipboard', 2000);
  }
});
