document.addEventListener('DOMContentLoaded', () => {
    const barraPesquisa = document.getElementById('barraPesquisa');
    
    
    if (!barraPesquisa) return; 

    
    const allProductsGridContainer = document.getElementById('allProductsGridContainer');
    const todosProdutosTitulo = document.getElementById('todosProdutosTitulo');
    
    
    const cards = document.querySelectorAll('#allProductsGridContainer .product-card');
    const semResultados = document.getElementById('semResultados');
    const categoryButtons = document.querySelectorAll('.category-button');

    
    const showAllProductsGrid = () => {
        
        allProductsGridContainer.style.display = 'flex'; 
        todosProdutosTitulo.style.display = 'block'; 
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
                card.style.display = 'block';
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
            
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            
            applyFilter();
        });
    });
});