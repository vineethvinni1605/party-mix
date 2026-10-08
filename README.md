# Party Mix

A real-time, room-code party game for 2–8 players, built with Node.js, Express, and Socket.IO.

## Requirements
- Node.js 20 or newer
- npm

## Run locally
1. Extract this ZIP.
2. Open a terminal in the `party-mix` folder.
3. Run `npm install`
4. Run `npm start`
5. Open `http://localhost:3000`

To play across devices on the same Wi-Fi, open the app using the host computer's local network IP address, for example `http://192.168.1.25:3000`, and allow Node.js through the computer's firewall if prompted.

## Play with friends over the internet
The server must be deployed to a Node.js host that supports persistent processes and WebSockets (for example, Render, Railway, or a VPS). Deploy the folder, set the start command to `npm start`, and share the deployed URL. This ZIP does not itself publish a public website.

## Game rounds
1. Quiz Clash
2. Guess the Word
3. Draw & Guess
4. Secret Spy
5. Speed Challenge

## Important prototype notes
- The project includes working room creation/joining, shared room state, timers, scoring, lobby, and a responsive interface.
- This is an initial playable prototype, not a production-audited service.
- Disconnect recovery retains the room entry for up to one minute, but full identity/session restoration across a browser refresh is not implemented.
- The round timers are server-authoritative. Drawing strokes and game submissions are broadcast over Socket.IO.
- Before public launch, strengthen reconnect identity, validate and rate-limit inputs, test simultaneous actions and edge cases, and review scoring for all player counts.
- No database is required for the initial in-memory prototype; active rooms are lost when the server restarts.
