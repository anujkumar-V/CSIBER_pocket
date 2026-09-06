// CSIBER//ONE Core Logic - CINEMATIC EDITION
const app = {
    socket: null,
    commands: [
        { name: "Overview Matrix", action: () => app.navigate('home') },
        { name: "Timetable Subsystem", action: () => app.navigate('timetable') },
        { name: "Attendance Guard", action: () => app.navigate('attendance') },
        { name: "Academic Calculator", action: () => app.navigate('sgpa') },
        { name: "Nexus Connect", action: () => app.navigate('connect') },
        { name: "Live Comms Link", action: () => app.navigate('chat') },
        { name: "Initialize AI", action: () => app.navigate('assistant') }
    ],

    init() {
        this.initThreeJS();
        this.initAmbientGlow();
        this.initTiltCards();
        this.initSocket();
        this.initCommandPalette();
        this.addSgpaRow(); this.addSgpaRow(); this.addCgpaRow();
        
        window.addEventListener('popstate', (e) => {
            if(e.state && e.state.section) this.showSection(e.state.section, false);
        });
    },

    navigate(section) {
        this.showSection(section, true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if(section === 'connect') this.loadPosts();
    },

    showSection(section, pushState = true) {
        document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
        document.getElementById(section).classList.add('active');
        if(pushState) history.pushState({section}, '', `#${section}`);
    },

    // --- HOLLYWOOD VFX: THREE.JS CGI RENDER ---
    initThreeJS() {
        const container = document.getElementById('webgl-container');
        if(!container) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        
        renderer.setSize(window.innerWidth, window.innerHeight);
        container.appendChild(renderer.domElement);

        // Create a Cinematic CGI Particle Core (Sphere)
        const geometry = new THREE.IcosahedronGeometry(2.5, 3);
        const material = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.02,
            transparent: true,
            opacity: 0.4
        });
        
        const particleCore = new THREE.Points(geometry, material);
        scene.add(particleCore);
        
        // Add subtle wireframe inner core
        const innerGeo = new THREE.IcosahedronGeometry(1.8, 1);
        const innerMat = new THREE.MeshBasicMaterial({ color: 0x3b82f6, wireframe: true, transparent: true, opacity: 0.1 });
        const innerMesh = new THREE.Mesh(innerGeo, innerMat);
        scene.add(innerMesh);

        camera.position.z = 6;

        let mouseX = 0;
        let mouseY = 0;
        document.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX / window.innerWidth) * 2 - 1;
            mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
        });

        // Animation Loop
        const animate = function () {
            requestAnimationFrame(animate);
            
            // Auto rotation
            particleCore.rotation.y += 0.002;
            particleCore.rotation.x += 0.001;
            innerMesh.rotation.y -= 0.003;
            innerMesh.rotation.x -= 0.002;

            // Interactive parallax
            particleCore.rotation.x += (mouseY * 0.5 - particleCore.rotation.x) * 0.05;
            particleCore.rotation.y += (mouseX * 0.5 - particleCore.rotation.y) * 0.05;
            
            renderer.render(scene, camera);
        };

        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    },

    // --- AMBIENT MOUSE GLOW (Vercel Style) ---
    initAmbientGlow() {
        const glow = document.getElementById('ambient-glow');
        window.addEventListener('mousemove', (e) => {
            glow.style.left = e.clientX + 'px';
            glow.style.top = e.clientY + 'px';
        });
    },

    // --- 3D CARD TILT EFFECT (Vanilla JS) ---
    initTiltCards() {
        const cards = document.querySelectorAll('.tilt-card');
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                // Calculate rotation (max 10 degrees)
                const xPct = (x / rect.width) - 0.5;
                const yPct = (y / rect.height) - 0.5;
                const rotateX = yPct * -10;
                const rotateY = xPct * 10;
                
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
                
                // Dynamic lighting inner glow based on mouse
                card.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.01) 60%)`;
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
                card.style.background = `rgba(255, 255, 255, 0.02)`; // Reset to var(--glass-bg)
            });
        });
    },

    // --- COMMAND PALETTE ---
    initCommandPalette() {
        const overlay = document.getElementById('cmd-overlay');
        const input = document.getElementById('cmd-input');
        const results = document.getElementById('cmd-results');

        window.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                overlay.style.display = 'flex';
                input.value = '';
                input.dispatchEvent(new Event('input'));
                input.focus();
            }
            if (e.key === 'Escape' && overlay.style.display === 'flex') {
                overlay.style.display = 'none';
            }
        });

        input.addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase();
            results.innerHTML = '';
            this.commands.filter(c => c.name.toLowerCase().includes(q)).forEach(cmd => {
                const div = document.createElement('div');
                div.className = 'cmd-item';
                div.innerHTML = `<span>${cmd.name}</span> <span class="dim" style="font-size:0.8em">JUMP</span>`;
                div.onclick = () => { cmd.action(); overlay.style.display = 'none'; };
                results.appendChild(div);
            });
        });
    },
    toggleCommandPalette() {
        document.dispatchEvent(new KeyboardEvent('keydown', {'key': 'k', 'ctrlKey': true}));
    },
    closeCommandPalette(e) {
        if(e && e.target !== document.getElementById('cmd-overlay')) return;
        document.getElementById('cmd-overlay').style.display = 'none';
    },

    // --- TIMETABLE ---
    async loadTimetable() {
        try {
            const res = await fetch('/api/timetable');
            const data = await res.json();
            const prog = document.getElementById('tt-prog').value;
            const batch = document.getElementById('tt-batch').value;
            const sem = document.getElementById('tt-sem').value;
            
            const grid = document.getElementById('tt-grid');
            grid.innerHTML = '';

            if(data[prog] && data[prog][batch] && data[prog][batch][sem]) {
                const days = data[prog][batch][sem];
                for (const [day, classes] of Object.entries(days)) {
                    let html = `<div class="day-card tilt-card"><h3>${day}</h3>`;
                    classes.forEach(c => {
                        html += `<div class="class-row">
                                    <div><strong>${c.subject}</strong> <br><span class="dim">${c.faculty}</span></div>
                                    <div style="text-align:right">${c.time}<br><span class="dim">${c.room}</span></div>
                                 </div>`;
                    });
                    html += `</div>`;
                    grid.innerHTML += html;
                }
                this.initTiltCards(); // Re-initialize tilt for new cards
            } else {
                grid.innerHTML = '<p class="dim">No data available for this selection.</p>';
            }
        } catch(e) {}
    },

    // --- ATTENDANCE ---
    calcAttendance() {
        const total = parseFloat(document.getElementById('att-total').value);
        const absent = parseFloat(document.getElementById('att-absent').value);
        const resBox = document.getElementById('att-result');

        if(isNaN(total) || isNaN(absent) || total <= 0) return;

        const present = total - absent;
        const perc = (present / total) * 100;
        
        let status = "", color = "", advice = "";
        if(perc >= 80) {
            status = "SAFE"; color = "#fff";
            let safeLeaves = Math.floor((present / 0.8) - total);
            advice = `You have ${safeLeaves} buffer leaves before reaching critical threshold.`;
        } else if (perc >= 75) {
            status = "WARNING"; color = "#fbbf24";
            advice = "Approaching limits. Maintain presence.";
        } else {
            status = "CRITICAL"; color = "#ef4444";
            let requiredClasses = Math.ceil((0.8 * total - present) / 0.2);
            advice = `Require ${requiredClasses} consecutive present days to restore status.`;
        }

        resBox.innerHTML = `
            <h3 style="color:${color}; font-size:2rem; margin-bottom:10px;">${perc.toFixed(2)}%</h3>
            <span style="border: 1px solid ${color}; color:${color}; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; text-transform: uppercase;">${status}</span>
            <p class="mt-1" style="font-size:0.9rem; color:var(--text-dim);">${advice}</p>
        `;
        resBox.classList.remove('hidden');
    },

    // --- GRADES ---
    switchGradeTab(tab) {
        document.querySelectorAll('.glass-tab').forEach(b => b.classList.remove('active'));
        event.target.classList.add('active');
        document.getElementById('sgpa-calc').classList.add('hidden');
        document.getElementById('cgpa-calc').classList.add('hidden');
        document.getElementById(`${tab}-calc`).classList.remove('hidden');
    },
    addSgpaRow() {
        const div = document.createElement('div');
        div.className = 'flex-between';
        div.innerHTML = `
            <input type="text" placeholder="Subject" style="flex:2">
            <input type="number" placeholder="Credits" class="sgpa-cr" style="flex:1">
            <input type="number" placeholder="Grade Pt" class="sgpa-gp" style="flex:1" max="10">
        `;
        document.getElementById('sgpa-rows').appendChild(div);
    },
    calcSgpa() {
        let totalCr = 0, totalPts = 0;
        document.querySelectorAll('#sgpa-rows .flex-between').forEach(row => {
            const cr = parseFloat(row.querySelector('.sgpa-cr').value);
            const gp = parseFloat(row.querySelector('.sgpa-gp').value);
            if(!isNaN(cr) && !isNaN(gp)) { totalCr += cr; totalPts += (cr * gp); }
        });
        const res = document.getElementById('sgpa-result');
        if(totalCr > 0) {
            let sgpa = (totalPts / totalCr).toFixed(2);
            res.innerHTML = `<h3 style="font-size:2rem">${sgpa} <span style="font-size:1rem; opacity:0.5;">SGPA</span></h3>`;
            res.classList.remove('hidden');
        }
    },
    addCgpaRow() {
        const div = document.createElement('div');
        div.className = 'flex-between';
        div.innerHTML = `
            <input type="text" placeholder="Semester" style="flex:2">
            <input type="number" placeholder="Total Credits" class="cgpa-cr" style="flex:1">
            <input type="number" placeholder="SGPA" class="cgpa-sgpa" style="flex:1">
        `;
        document.getElementById('cgpa-rows').appendChild(div);
    },
    calcCgpa() {
        let totalCr = 0, totalPts = 0;
        document.querySelectorAll('#cgpa-rows .flex-between').forEach(row => {
            const cr = parseFloat(row.querySelector('.cgpa-cr').value);
            const sgpa = parseFloat(row.querySelector('.cgpa-sgpa').value);
            if(!isNaN(cr) && !isNaN(sgpa)) { totalCr += cr; totalPts += (cr * sgpa); }
        });
        const res = document.getElementById('cgpa-result');
        if(totalCr > 0) {
            let cgpa = (totalPts / totalCr).toFixed(2);
            res.innerHTML = `<h3 style="font-size:2rem">${cgpa} <span style="font-size:1rem; opacity:0.5;">CGPA</span></h3>`;
            res.classList.remove('hidden');
        }
    },

    // --- CLASS CONNECT ---
    togglePostModal() {
        document.getElementById('post-modal').classList.toggle('hidden');
    },
    async submitPost() {
        const author = document.getElementById('post-author').value;
        const cat = document.getElementById('post-category').value;
        const msg = document.getElementById('post-msg').value;
        const file = document.getElementById('post-file').files[0];

        if(!msg) return alert("Log details cannot be empty.");

        const fd = new FormData();
        fd.append('author', author); fd.append('category', cat); fd.append('message', msg);
        if(file) fd.append('file', file);

        try {
            const res = await fetch('/api/posts', { method: 'POST', body: fd });
            if(res.ok) {
                this.togglePostModal();
                document.getElementById('post-msg').value = '';
                this.loadPosts();
            }
        } catch(e) {}
    },
    async loadPosts() {
        try {
            const res = await fetch('/api/posts');
            const posts = await res.json();
            const grid = document.getElementById('posts-feed');
            grid.innerHTML = '';
            posts.forEach(p => {
                let fileHtml = p.file_url ? `<a href="${p.file_url}" target="_blank" style="color:var(--accent); text-decoration:none; font-size:0.85rem; margin-top:15px; display:inline-block;">↳ Open Attachment</a>` : '';
                grid.innerHTML += `
                    <div class="post-card glass-card tilt-card">
                        <div class="post-meta">
                            <span><strong style="color:#fff">${p.author}</strong> // ${p.category}</span>
                            <span>${p.timestamp.split(' ')[0]}</span>
                        </div>
                        <p style="font-size:1.05rem">${p.message.replace(/</g, "&lt;")}</p>
                        ${fileHtml}
                    </div>
                `;
            });
            this.initTiltCards();
        } catch(e) {}
    },

    // --- CHAT & SOCKET.IO ---
    initSocket() {
        this.socket = io();
        this.socket.on('chat_history', msgs => {
            const box = document.getElementById('chat-messages');
            box.innerHTML = '';
            msgs.forEach(m => this.appendChat(m.author, m.message, m.timestamp));
            box.scrollTop = box.scrollHeight;
        });
        this.socket.on('new_message', m => {
            this.appendChat(m.author, m.message, m.timestamp);
            const box = document.getElementById('chat-messages');
            box.scrollTop = box.scrollHeight;
        });
    },
    appendChat(author, msg, time) {
        const box = document.getElementById('chat-messages');
        const div = document.createElement('div');
        div.className = 'msg';
        div.innerHTML = `
            <div class="msg-info">${author} • ${time}</div>
            <div class="msg-bubble">${msg.replace(/</g, "&lt;")}</div>
        `;
        box.appendChild(div);
    },
    sendChatMessage() {
        const name = document.getElementById('chat-name').value;
        const msgInput = document.getElementById('chat-msg');
        if(msgInput.value.trim()) {
            this.socket.emit('send_message', { author: name, message: msgInput.value });
            msgInput.value = '';
        }
    },
    checkChatEnter(e) { if(e.key === 'Enter') this.sendChatMessage(); },

    // --- ASSISTANT ---
    async askAi() {
        const input = document.getElementById('ai-input');
        const query = input.value.trim();
        if(!query) return;

        const box = document.getElementById('ai-messages');
        box.innerHTML += `<div class="msg" style="text-align:right"><div class="msg-bubble" style="background:var(--glass-highlight);display:inline-block">${query.replace(/</g, "&lt;")}</div></div>`;
        input.value = '';
        box.scrollTop = box.scrollHeight;

        try {
            const res = await fetch('/api/assistant', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query})
            });
            const data = await res.json();
            
            setTimeout(() => {
                box.innerHTML += `<div class="msg ai"><div class="msg-bubble">${data.response}</div></div>`;
                box.scrollTop = box.scrollHeight;
            }, 600); 
        } catch(e) {}
    },
    checkAiEnter(e) { if(e.key === 'Enter') this.askAi(); }
};

window.onload = () => app.init();