// =========================================================
// ✅ Live Thinking Visualizer (Plug & Play)
// =========================================================

(function () {

    // Auto-create board if not exists
    function createBoard() {
        let board = document.getElementById("thinking-board");

        if (!board) {
            board = document.createElement("div");
            board.id = "thinking-board";

            board.style.width = "100%";
            board.style.height = "400px";
            board.style.border = "1px solid #ccc";
            board.style.marginTop = "20px";
            board.style.position = "relative";
            board.style.overflow = "auto";

            document.body.appendChild(board);
        }

        return board;
    }

    // Render Flow
    function renderFlow(flow) {
        const board = createBoard();
        board.innerHTML = "";

        if (!flow || !flow.nodes) return;

        const nodeElements = {};

        // Create nodes
        flow.nodes.forEach((node, index) => {
            const div = document.createElement("div");

            div.innerText = node.label;
            div.title = node.full_text;

            div.style.position = "absolute";
            div.style.padding = "10px";
            div.style.background = "#4f46e5";
            div.style.color = "#fff";
            div.style.borderRadius = "8px";
            div.style.fontSize = "12px";
            div.style.cursor = "pointer";

            // Auto layout
            div.style.left = (index * 180 + 20) + "px";
            div.style.top = "120px";

            board.appendChild(div);
            nodeElements[node.id] = div;
        });

        // Draw arrows
        const canvas = document.createElement("canvas");
        canvas.width = board.scrollWidth;
        canvas.height = board.scrollHeight;
        canvas.style.position = "absolute";
        canvas.style.top = "0";
        canvas.style.left = "0";

        board.appendChild(canvas);

        const ctx = canvas.getContext("2d");

        flow.edges.forEach(edge => {
            const from = nodeElements[edge.from];
            const to = nodeElements[edge.to];

            if (!from || !to) return;

            const x1 = from.offsetLeft + from.offsetWidth;
            const y1 = from.offsetTop + from.offsetHeight / 2;

            const x2 = to.offsetLeft;
            const y2 = to.offsetTop + to.offsetHeight / 2;

            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.strokeStyle = "#000";
            ctx.lineWidth = 2;
            ctx.stroke();
        });
    }

    // =========================================================
    // ✅ AUTO HOOK INTO /ask RESPONSE (NO CODE CHANGE NEEDED)
    // =========================================================
    const originalFetch = window.fetch;

    window.fetch = async function (...args) {
        const response = await originalFetch(...args);

        try {
            const url = args[0];

            if (typeof url === "string" && url.includes("/ask")) {
                const cloned = response.clone();
                const data = await cloned.json();

                if (data.flow) {
                    renderFlow(data.flow);
                }
            }
        } catch (e) {
            console.log("Visualizer Error:", e);
        }

        return response;
    };

})();