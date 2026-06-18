#**THIS IS DEAD**
# SemCAS‑Web
A natural‑language Computer Algebra System (CAS) for the browser — built by Sem, powered by Nerdamer, and designed to understand math written the way humans actually speak.

SemCAS‑Web lets you type things like:

> “differentieer x^2 + 3x”  
> “wat is de integraal van sin x”  
> “los x^2 = 9 op”

…and instantly returns the correct mathematical result.

---

## ⭐ Features
- Natural‑language → math parser  
- Supports: differentiation, integration, solving, factoring, expanding, simplifying  
- Automatic syntax correction (implicit multiplication, `sin x` → `sin(x)`, `x²` → `x^2`, etc.)  
- Powered by Nerdamer CAS engine  
- Clickable history panel  
- Fully client‑side (no backend required)  
- Works on desktop, tablet, and mobile

---

## 🚀 Live Demo  
**https://semalewijnse2014-prog.github.io/SemCas-Web/**

---

## 📦 Installation
No installation required — simply open `index.html` in your browser.

To run locally:
git clone https://github.com//SemCAS-Web cd SemCAS-Web open index.html
---

## 🧠 How It Works
SemCAS‑Web uses:

- A custom natural‑language parser (SemParser v3)  
- A syntax normalizer that cleans and fixes algebra  
- Nerdamer for symbolic math operations  

The parser interprets Dutch sentences and converts them into valid Nerdamer expressions.

---

# 📘 Syntax: Dutch  
### *(Currently the only supported language — English support planned for a future release)*

This section explains the **Dutch syntax**, but the explanation itself is written in **English** so international developers can understand how SemCAS‑Web works.

---

## 🇳🇱 Dutch Syntax Rules (Explained in English)

### **1. Differentiation**
Trigger words:
- `differentieer`
- `afgeleide`
- `wat is de afgeleide van`
- `deriveer`

**Examples:**
- `differentieer x^2 + 3x` → `diff(x^2 + 3x, x)`
- `wat is de afgeleide van sin x` → `diff(sin(x), x)`

---

### **2. Integration**
Trigger words:
- `integreer`
- `integraal`
- `wat is de integraal van`
- `bereken de integraal van`

**Examples:**
- `integreer x^2` → `integrate(x^2, x)`
- `wat is de integraal van sin(x)` → `integrate(sin(x), x)`

---

### **3. Solving Equations**
Trigger words:
- `los ... op`
- `kun je ... oplossen`

**Examples:**
- `los x^2 = 9 op` → `solve(x^2 = 9, x)`
- `kun je x+5=12 oplossen` → `solve(x+5=12, x)`

---

### **4. Expanding**
Trigger words:
- `breid uit`
- `expand`

**Example:**
- `breid uit (x+2)^3` → `expand((x+2)^3)`

---

### **5. Factoring**
Trigger words:
- `factoriseer`
- `factor`
- `ontbind`

**Example:**
- `factoriseer x^2+5x+6` → `factor(x^2+5x+6)`

---

### **6. Simplifying**
Trigger words:
- `vereenvoudig`
- `herleid`

**Example:**
- `vereenvoudig 2x + 3x` → `simplify(2x + 3x)`

---

### **7. Limits**
Trigger pattern:
- `limiet van <expr> als <var> naar <value>`

**Example:**
- `limiet van sin x / x als x naar 0` → `limit(sin(x)/x, x, 0)`

---

## 🔧 Automatic Syntax Fixes
SemCAS‑Web automatically corrects:

- `sin x` → `sin(x)`
- `2x` → `2*x`
- `x2` → `x*2`
- `(x+1)(x+2)` → `(x+1)*(x+2)`
- `x²` → `x^2`
- Removes punctuation (`?`, `!`, `.`, etc.)
- Normalizes whitespace  
- Prevents invalid variables like `x?`

---

---

## 🧩 Dependencies
- Nerdamer (Algebra, Calculus, Solve, Extra modules) — loaded via CDN

---

## 🧑‍💻 Contributing
Pull requests are welcome.  
If you want to help add **English syntax support**, open an issue first so we can coordinate.

---

## 📄 License
GPLv3

---

## 🧨 Credits
Built by **Sem**  
Parser design, UI, and chaotic debugging powered by pure Sem‑energy.  
Math engine powered by Nerdamer.
