# Contributting.md para o Mercado Cesar

O Mercado Cesar foi desenvolvido com o intuito de aprimorar o processo de compra e revenda online, com suas próprias capacidades e tecnologias, contendo processos e desenvolvimentos até então únicos.
Bem vindos ao futuro do comércio eletrônico.

## Tabela de conteúdos

- [Iniciando](#iniciando):
  - [1 Crie uma pasta](#1-crie-uma-pasta)
  - [2 Clone esse repositório](#2-clone-esse-repositório)
  - [3 Crie um arquivo .env](#3-crie-um-arquivo-.env)
  - [4 Crie um ambiente virtual](#4-crie-um-ambiente-virtual)
  - [5 Abra o ambiente virtual](#5-abra-o-ambiente-virtual)
  - [6 Instale as dependências](#6-instale-as-dependências)
  - [7 Ative a IDE de programação a sua escolha](#7-ative-a-ide-de-programação-a-sua-escolha)
  - [8 Para ativar o software no sistema](#8-para-ativar-o-software-no-sistema)
- [Como contribuir](#como-contribuir)
  - [Fork](#fork-você-pode-criar-uma-cópia-pessoal-do-nosso-repositório-através-do-recurso-fork)
  - [Pull Requests](#pull-requests-depois-de-fazer-as-suas-modificações-no-código-da-sua-cópia-dependendo-se-sua-versão-estiver-funcionando)

- [Problemas Comuns](#problemas-comuns)

   - [Resolvendo Erros de Carregamento Genéricos](#resolvendo-erros-de-carregamento-genéricos) 

   - [Reportando Bugs e Problemas Persistentes](#reportando-bugs-e-problemas-persistentes)

   - [Falhas do Django](#falhas-do-django)

   - [Lidando com a demora de carregamento inicial da Aplicação web](#lidando-com-a-demora-de-carregamento-inicial-da-aplicacao-web)

- [Como reportar bugs e falhas](#como-reportar-bugs-e-falhas)

- [Referências](#referências)


# Iniciando:
Para iniciar o sistema, siga as seguintes instruções

## 1 Crie uma pasta
Primeiro, você precisa criar uma pasta.

Ao acessar o sistema de arquivos, vá ao arquivo do sistema, e crie uma pasta.

Depois de criar uma pasta, é necessário acessar a pasta, e executar alguns comandos, por meio do prompt de comandos: 
Acessando a pasta, digite como escrito abaixo :
	
    cmd 
Esse comando quando digitado, vai abrir o terminal de comandos do Windows 

## 2 Clone esse repositório
    
    git clone https://github.com/GabrielNFR/Mercado-Cesar.git

## 3 Crie um arquivo .env
Usando o prompt de comandos, escreva: 

     cd Mercado-Cesar
Em seguida, use o seguinte comando para criar o arquivo.env(ou crie manualmente pelo vscode):
Na versão de Windows:
     
     echo.>.env
No Linux/Mac:
   
     touch .env
Em seguida, abra o arquivo .env e cole o código abaixo:

     #Configurações de Desenvolvimento Local
     DEBUG=True
     SECRET_KEY=django-insecure-)gnreljovb28r9^h^@hi9y)p-+y4l2v7!t3mu19s7@f@5ns#bl

     #Cloudinary - Usar as mesmas credenciais de produção para desenvolvimento local
     CLOUDINARY_CLOUD_NAME=dgnybb784
     CLOUDINARY_API_KEY=332145282913276
     CLOUDINARY_API_SECRET=st8kV9cIDNzhwNaw415JcdIJq9z4

     #Hosts permitidos
     ALLOWED_HOSTS=localhost,127.0.0.1
## 4 Crie um ambiente virtual
Windows:
     
     py -m venv venv
Para  Linux/Mac:
     
     python3 -m venv venv
## 5 Abra o ambiente virtual
Depois de criar é necessário acessar e usar a venv.
No Windows:
     
     venv\Scripts\activate

No Linux/Mac:
   
     source venv/bin/activate

## 6 Instale as dependências
Para realizar isso, abra o terminal de prompt. Nele, digite o seguinte comando:
     
     pip install -r requirements.txt
Esse comando fará a coleta dos requerimentos e o instalamento automático.

## 7 Ative a IDE de programação a sua escolha
No terminal de prompt, para abrir a IDE de Programação que você usa, exemplo do caso do VsCode, utilize o comando a seguir (Verifique se está dentro da pasta ainda):     
                                        
    code .
Esse comando ativará automaticamente o Visual Studio Code.

## 8 Para ativar o software no sistema
   Para iniciar o servidor, através do Django, depois que todas as configurações anteriores forem executadas com sucesso, é utilizado o manage.py. 

O arquivo Manage.py é um dos mais importantes dentro do sistema. 

Por ele, o sistema(em modo de teste, via Django) pode ser ativado, para mostrar o site, assim como outras funções necessárias também perpassam por ele (como o sistema de migrações).

Em outras palavras, o Manage.py é o cérebro do sistema, logo, a parte mais importante e sensível do sistema.

Não se deve modificar, exceto necessário, o manage.py, pois erros imprevisíveis e inesperados podem acontecer.

Para iniciar, digite no terminal do prompt de comandos do Windows, Mac,Linux:
         
    py manage.py runserver
Este comando iniciará o servidor em uma aba própria. Basta clicar no link que aparecerá. Nele estará escrito algo como: 
                       
    https:\\1.20007.08	
# Como contribuir:

  O código-fonte do Mercado Cesar está público, então quem quiser, pode contribuir diretamente para o desenvolvimento dele, caso possuam conhecimento técnico.

• Como Contribuir (Código): A maneira de contribuir é através de duas formas principais:

### Fork: Você pode criar uma cópia pessoal do nosso repositório através do recurso Fork

(na página principal do Github, está o comando de criar o Fork), 

Ou acesse rapidamente por [aqui](https://github.com/GabrielNFR/Mercado-Cesar/fork)

### Pull Requests: Depois de fazer as suas modificações no código da sua cópia (dependendo se sua versão estiver funcionando)

Você pode enviar suas alterações para a revisão e poderem ser incorporadas ao projeto principal através de Pull requests, se aprovadas na revisão.

 Regras para as pull requests sejam aprovadas:
 >    Ao executar os commits, registre uma descrição no commit, com as mudanças que você fez, e alguma forma de contato (De preferência, email).

 >    Após enviar, o resultado da avaliação será repassado a você entre 3 ou 5 dias depois,

 >    E, após isso, será feita a incorporação das mudanças feitas.

• Ferramentas de Desenvolvimento Rápido: 

Para quem deseja contribuir rapidamente, basta utilizar o Codespaces (Para aprender mais sobre codespaces, acesse as referências ou clique [aqui](https://docs.github.com/pt/codespaces)), que fornecem ambientes de desenvolvimento instantâneos, e Actions (Sobre o GitHub actions, acesse as referências ou clique [aqui](https://docs.github.com/pt/actions))

  >Codespaces funcionam como um ambiente de desenvolvimento completo na nuvem, executado em máquinas virtuais e contêineres do Docker, que permite codificar, testar e depurar sem a necessidade de configurar um ambiente local complexo.

# Problemas comuns

   O Mercado Cesar é um site desenvolvido para otimizar a experiência de compra. 
   Se você encontrar dificuldades, siga estas etapas simples para resolver e/ou reportar o problema.

### Falhas do Django
> O problema mais comum de acontecer: O Django, por ser uma ferramenta de desenvolvimento sensível à modificações, pode apresentar problemas imprevistos.
  
> Então, em caso de versões obsoletas, utilize o comando “discard current changes” para descartar novas modificações.
  
> Depois, utilize o comando 
                    
    git pull
    
   para puxar, diretamente do github, a atual versão do código. 
     
Se não for isso, basta reaplicar o comando:

    py manage.py runserver
Que, em caso de problema resolvido, o servidor voltará a funcionar.

### Resolvendo Erros de Carregamento Genéricos
  > Se você estiver visualizando partes da página ou painéis que não carregam corretamente (erro 404), ou receber mensagens de erro alternativas como "Uh oh! Houve um erro ao carregar", a solução imediata é simples:

• A Solução: Recarregue a página.
        
Se o problema persistir após recarregar, prossiga para a próxima etapa.

### Reportando Bugs e Problemas Persistentes:
   > Se você encontrar um erro que não se resolve esperando ou recarregando, é crucial reportar para a equipe de desenvolvimento, [aqui](como-reportar-bugs-e-falhas)

### Lidando com a demora de carregamento inicial da Aplicacao web

   > O segundo problema mais comum que você pode encontrar é um atraso significativo ao tentar acessar o site em produção. Nesse caso, isso ocorre devido à característica do ambiente onde o sistema está hospedado.

>   • O Problema: Nossa aplicação em produção utiliza um plano gratuito de hospedagem (Render). Após um período sem atividade, o sistema entra em "hibernação" (dorme).

>   • A Solução: Se você acessar a aplicação nesse estado, é necessário esperar entre 1 a 2 minutos para que ela "acorde" e carregue completamente.


>    • Link da Aplicação em Produção: 🔗 [versão em produção](mercado-cesar.onrender.com)

# Como reportar bugs e falhas

   O Mercado Cesar utiliza um sistema específico para rastrear e gerenciar falhas:

   • Ferramenta de Rastreamento: Utilize o Controle de [Issues](https://github.com/GabrielNFR/Mercado-Cesar/issues)/Bug Tracker da equipe. 

Esse é o canal oficial para que nós, a equipe, acompanhemos o ciclo de vida do erro (desde a identificação do erro, até que agirmos para podermos resolvê-lo), e assim, as mudanças/correções podem ser realizadas e concluídas o mais rápido possível.

Escreva com bastante atenção e com bastante detalhes, e se possível, tire prints do que aconteceu.  

Dica de especialista: Diga o que você estava tentando fazer, qual funcionalidade falhou (ex: login/registro, gerenciamento de estoque, busca de produtos) e qual mensagem de erro apareceu,tudo com bastante atenção e com muitos detalhes, e, se possível, tire prints do erro, e as envie por meio das [Issues](https://github.com/GabrielNFR/Mercado-Cesar/issues).	 

Isso nos ajuda (a Equipe de Desenvolvimento) para podermos replicar, avaliar, compreender e corrigir o erro rapidamente.

• Outras Vias de Suporte (Geral): 
Embora o rastreador de issues seja o local ideal para bugs específicos do código, se você tiver feedback geral ou precisar de suporte, o GitHub (plataforma onde o código está hospedado) oferece outras vias, como:

◦ Fórum da Comunidade.

◦ Opção de Fornecer Feedback (para a plataforma GitHub em geral, sobre o uso de recursos como a sintaxe de busca)

# Referências
	
README.md:[README.md](https://github.com/GabrielNFRMercado-Cesar/blob/prod/README.md)


Solicitações de pull:[pull request](https://docs.github.com/pt/pull-requests)


Codespaces:[Os Codespaces](https://docs.github.com/pt/codespaces),  [vídeo sobre codespaces](https://www.youtube.com/watch?v=X7jErg2jZ44&t=411)



