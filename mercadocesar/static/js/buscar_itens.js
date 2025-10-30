document.addEventListener('DOMContentLoaded', () => {
    const barraPesquisa = document.getElementById('barraPesquisa');
    
    
    if (!barraPesquisa) return;

    
    const allProductsGridContainer = document.getElementById('allProductsGridContainer');
    const todosProdutosTitulo = document.getElementById('todosProdutosTitulo');
    
    
    const cards = document.querySelectorAll('#allProductsGridContainer .product-card');
    const semResultados = document.getElementById('semResultados');
    const categoryButtons = document.querySelectorAll('.category-button');

    
    const showAllProductsGrid = () => {
        // Mostrar o container principal como block para que o grid interno funcione
        allProductsGridContainer.style.display = 'block'; 
        todosProdutosTitulo.style.display = 'flex'; 
    };

    const applyFilter = () => {
        const searchTerm = barraPesquisa.value.toLowerCase().trim();
        const activeButton = document.querySelector('.category-button.active');
       
        const activeCategory = activeButton ? activeButton.getAttribute('data-filter').toLowerCase() : 'all';
        
        showAllProductsGrid(); 
        
        let foundCount = 0;

        cards.forEach(card => {
            
            const nomeElement = card.querySelector('.nomeProduto');
            const nomeProduto = nomeElement ? nomeElement.textContent.toLowerCase() : '';
            
            const cardCategory = card.getAttribute('data-categoria').toLowerCase();

            const matchesCategory = activeCategory === 'all' || cardCategory === activeCategory;

            
            const matchesSearch = nomeProduto.includes(searchTerm);

           
            if (matchesCategory && matchesSearch) {
                // Não sobrescrever o display - deixar o grid funcionar
                card.style.display = '';
                foundCount++;
            } else {
                card.style.display = 'none';
            }
        });

        
        if (semResultados) {
            if (foundCount === 0) {
                semResultados.style.display = 'block';
            } else {
                semResultados.style.display = 'none';
            }
        }
    };

    barraPesquisa.addEventListener('keyup', applyFilter);

   
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remover active de todos os botões
            categoryButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.style.backgroundColor = 'white';
                btn.style.color = '#374151';
                btn.style.borderColor = '#d1d5db';
            });
            
            // Adicionar active ao botão clicado
            button.classList.add('active');
            button.style.backgroundColor = '#f4a361';
            button.style.color = 'white';
            button.style.borderColor = '#f4a361';

            // Aplicar filtro
            applyFilter();
        });
    });

});
