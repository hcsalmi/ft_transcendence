# ft_transcendence
TRANCE ENERGY 2024
Contributors: jnsh, kenlies, dardangerguri, l-broms, hcsalmi



This is a Hive Helsinki project for creating a website for Pong. The following mandatory requirements were specified in the subject.
General requirements:
- The frontend should be developed using pure vanilla Javascript.
- The website must be a single-page application. The user should be able to use the Back and Forward buttons of the browser.
- The website must be compatible with the latest stable up-to-date version of Google Chrome.
- The user should encounter no unhandled errors and no warnings when browsing the website.
- Everything must be launched with a single command line to run an autonomous container provided by Docker. Example : docker-compose up --build

Game requirements:
The main purpose of this website is to play Pong versus other players.
- Users must have the ability to participate in a live Pong game against another player directly on the website. Both players will use the same keyboard. The Remote players module can enhance this functionality with remote players.
- A player must be able to play against another player, but it should also be possible to propose a tournament. This tournament will consist of multiple players who can take turns playing against each other. You have flexibility in how you implement the tournament, but it must clearly display who is playing against whom and the order of the players.
- A registration system is required: at the start of a tournament, each player must input their alias name. The aliases will be reset when a new tournament begins. However, this requirement can be modified using the Standard User Management module.
- There must be a matchmaking system: the tournament system organize the matchmaking of the participants, and announce the next fight.
- All players must adhere to the same rules, which includes having identical paddle speed. This requirement also applies when using AI; the AI must exhibit the same speed as a regular player.
- The game itself must be developed in accordance with the default frontend constraints (as outlined above), or you may choose to utilize the FrontEnd module, or you have the option to override it with the Graphics module. While the visual aesthetics can vary, it must still capture the essence of the original Pong (1972).


Security concerns:
- Any password stored in the database, if applicable, must be hashed.
- The website must be protected against SQL injections/XSS.
- If there is a backend or any other features, it is mandatory to enable an HTTPS connection for all aspects (Utilize wss instead of ws...).
- Some form of validation for forms and any user input must be included, either within the base page if no backend is used or on the server side if a backend is employed.
- Regardless of whether you choose to implement the JWT Security module with 2FA, it’s crucial to prioritize the security of your website. For instance, if you opt to create an API, ensure your routes are protected. Even if no JWT tokens are used, securing the site remains essential.

Bonus features we decided to include:
- Major module: Use Django framework as backend
- Minor module: Use a PostgreSQL database for the backend
- Major module: Standard user management, authentication, users across tournaments
  ◦ Users can subscribe to the website and log in a securely.
  ◦ Users can select a unique display name to play the tournaments.
  ◦ Users can update their information.
  ◦ Users can upload an avatar, with a default option if none is provided.
  ◦ Users can add others as friends and view their online status.
  ◦ User profiles display stats, such as wins and losses.
  ◦ Each user has a Match History including 1v1 games, dates, and relevant details, accessible to logged-in users.
- Major module: Remote players (players using separate computers, accessing the same website and playing the same Pong game)
- Minor module: Game Customization Options (e.g. custom speed)
- Major module: Live chat (sending direct messages, blocking other users, sending game invites, accessing other users' information through chat interface, getting notifications of upcoming matches)
- Major module: Introduce an AI Opponent
- Major module: Designing the Backend as Microservices (loosely coupled microservices with well-defined tasks and scalability)
- Major module: Replacing Basic Pong with Server-Side Pong and Implementing an API (develop server-side logic for the Pong game, implement API)
- Major module: Enabling Pong Gameplay via CLI against Web Users with API Integration (develop a Command-Line Interface (CLI) aloowing users to play Pong against players using the web version of the game)
- Minor module: Expanding Browser Compatibility (Firefox-compatibility)


Due to this repository being a copy of the original repo, the git commits are not attributed correctly. In this project, I was mostly involved with working on back-end features (microservices), server-side pong and CLI client for the Pong.

