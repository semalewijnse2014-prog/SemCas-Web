# ============================================
#   SemCAS 11.1 — Blok 1: Basis + StapGenerator + Templates + CAS
# ============================================

import sympy as sp
import re
from sympy import sympify, SympifyError

ANGLE_MODE = "rad"

# Variabelen
letters = "abcdefghijklmnopqrstuvwxyz"
letters = letters.replace("a", "").replace("b", "").replace("c", "").replace("E", "")
symbols = {ch: sp.Symbol(ch) for ch in letters}
symbols["E"] = sp.E
symbols["pi"] = sp.pi
symbols["phi"] = (1 + sp.sqrt(5)) / 2
symbols["I"] = sp.I
symbols["oo"] = sp.oo
symbols["∞"] = sp.oo
symbols["inf"] = sp.oo
symbols["infinity"] = sp.oo

def naar_rad(x):
    if ANGLE_MODE == "deg":
        return x * sp.pi / 180
    return x

def trig_fix(e):
    if ANGLE_MODE == "rad":
        return e
    return e.replace(
        lambda ex: isinstance(ex, sp.Function) and ex.func in (sp.sin, sp.cos, sp.tan, sp.csc, sp.sec, sp.cot),
        lambda f: f.func(naar_rad(f.args[0]))
    )

def fix_input(s):
    s = s.replace("∞", " OO_CONST ")
    s = re.sub(r"\binf\b", " OO_CONST ", s)
    s = re.sub(r"\binfinity\b", " OO_CONST ", s)
    s = re.sub(r"\boo\b", " OO_CONST ", s)
    s = s.replace("E", " E_CONST ")
    
    func_map = {
        "sin": "§1§", "cos": "§2§", "tan": "§3§",
        "csc": "§4§", "sec": "§5§", "cot": "§6§",
        "log": "§7§", "ln": "§7§", "sqrt": "§8§", "root": "§9§",
        "arcsin": "§10§", "arccos": "§11§", "arctan": "§12§",
        "sinh": "§13§", "cosh": "§14§", "tanh": "§15§",
    }
    for f, m in func_map.items():
        s = re.sub(rf"\b{f}\s*\(", f"{m}(", s)
    
    s = s.replace("pi", " PI_CONST ").replace("phi", " PHI_CONST ").replace("I", " I_CONST ")
    s = s.replace("^", "**")
    s = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", s)
    s = re.sub(r"([a-zA-Z])(\d)", r"\1*\2", s)
    s = re.sub(r"\b([d-z])([d-z])\b", r"\1*\2", s)
    
    s = s.replace("PI_CONST", "pi").replace("PHI_CONST", "phi").replace("I_CONST", "I")
    
    rev = {
        "§1§": "sin", "§2§": "cos", "§3§": "tan",
        "§4§": "csc", "§5§": "sec", "§6§": "cot",
        "§7§": "log", "§8§": "sqrt", "§9§": "root",
        "§10§": "asin", "§11§": "acos", "§12§": "atan",
        "§13§": "sinh", "§14§": "cosh", "§15§": "tanh",
    }
    for m, f in rev.items():
        s = s.replace(m, f)
    
    s = s.replace("E_CONST", "E").replace("OO_CONST", "oo")
    return s

def pretty(expr):
    s = str(expr)
    s = s.replace("**", "^")
    s = re.sub(r"(\d+)\*([a-zA-Z])", r"\1\2", s)
    s = re.sub(r"([a-zA-Z])\*(\d+)", r"\2\1", s)
    s = re.sub(r"([a-zA-Z])\*([a-zA-Z])", r"\1\2", s)
    s = s.replace("log", "ln")
    s = s.replace("asin", "arcsin").replace("acos", "arccos").replace("atan", "arctan")
    return s

def expr(s):
    try:
        return sp.sympify(fix_input(s), symbols)
    except SympifyError:
        raise

# --------------------------------------------
# StapGenerator - Uitgebreid
# --------------------------------------------
class StapGenerator:
    def __init__(self):
        self.stappen = []
        self.diepte = 0
        self.teller = 0
        self.substituties = {}
    
    def voeg_stap_toe(self, template, **kwargs):
        self.teller += 1
        uitgewerkt = self._render_template(template, **kwargs)
        indent = "  " * self.diepte
        self.stappen.append(f"{indent}{uitgewerkt}")
        return uitgewerkt
    
    def _render_template(self, template, **kwargs):
        result = template
        for key, value in kwargs.items():
            if hasattr(value, '_sympy_') or isinstance(value, (sp.Expr, sp.Basic, sp.Pow, sp.Mul, sp.Add)):
                value = pretty(value)
            elif isinstance(value, (list, tuple)):
                if len(value) > 3:
                    waarden = [str(v) for v in value[:3]]
                    value = ", ".join(waarden) + ", ..."
                else:
                    value = ", ".join(str(v) for v in value)
            elif isinstance(value, bool):
                value = "ja" if value else "nee"
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def toon_stappen(self, titel="📝 Stap-voor-stap oplossing"):
        if not self.stappen:
            return "Geen stappen nodig (direct resultaat)."
        output = [titel, "=" * len(titel), ""]
        for i, stap in enumerate(self.stappen, 1):
            output.append(f"{i}. {stap}")
        return "\n".join(output)
    
    def reset(self):
        self.stappen = []
        self.diepte = 0
        self.teller = 0
        self.substituties = {}
    
    def verdiep(self):
        self.diepte += 1
    
    def verdiep_uit(self):
        self.diepte = max(0, self.diepte - 1)
    
    def voeg_substitutie(self, naam, waarde):
        self.substituties[naam] = waarde
    
    def krijg_substitutie(self, naam):
        return self.substituties.get(naam, naam)

# --------------------------------------------
# COMPLETE TEMPLATE DATABASE
# --------------------------------------------
TEMPLATES = {
    # Differentiëren - Basis
    "diff_power": "Pas de **machtregel** toe: d/dx[{x}^{n}] = {n}·{x}^{{n-1}} → {resultaat}",
    "diff_const": "Afgeleide van een constante is 0: d/dx[{c}] = 0",
    "diff_sum": "Differentieer **term voor term**: d/dx[{a} + {b}] = {a'} + {b'}",
    "diff_product": "Gebruik de **productregel**: d/dx[{f}·{g}] = {f'}·{g} + {f}·{g'} → {resultaat}",
    "diff_quotient": "Gebruik de **quotiëntregel**: d/dx[{f}/{g}] = ({f'}·{g} - {f}·{g'})/{g}² → {resultaat}",
    "diff_chain": "Pas de **kettingregel** toe: d/dx[{f}({g})] = {f'}({g})·{g'} → {resultaat}",
    "diff_chain_power": "Pas **kettingregel** toe op macht: d/dx[{base}^{exp}] = {exp}·{base}^{{exp-1}}·{base'} → {resultaat}",
    
    # Differentiëren - Exponentieel en Logaritmisch
    "diff_exp": "Afgeleide van e^u: d/dx[e^{u}] = e^{u}·u' → {resultaat}",
    "diff_exp_base": "Afgeleide van {a}^{u}: d/dx[{a}^{u}] = {a}^{u}·ln({a})·u' → {resultaat}",
    "diff_ln": "Afgeleide van ln(u): d/dx[ln({u})] = {u'}/{u} → {resultaat}",
    "diff_log": "Afgeleide van log_{a}(u): d/dx[log_{a}({u})] = {u'}/({u}·ln({a})) → {resultaat}",
    
    # Differentiëren - Goniometrisch
    "diff_sin": "Afgeleide van sin(u): d/dx[sin({u})] = cos({u})·u' → {resultaat}",
    "diff_cos": "Afgeleide van cos(u): d/dx[cos({u})] = -sin({u})·u' → {resultaat}",
    "diff_tan": "Afgeleide van tan(u): d/dx[tan({u})] = sec²({u})·u' → {resultaat}",
    "diff_csc": "Afgeleide van csc(u): d/dx[csc({u})] = -csc({u})·cot({u})·u' → {resultaat}",
    "diff_sec": "Afgeleide van sec(u): d/dx[sec({u})] = sec({u})·tan({u})·u' → {resultaat}",
    "diff_cot": "Afgeleide van cot(u): d/dx[cot({u})] = -csc²({u})·u' → {resultaat}",
    
    # Differentiëren - Inverse Goniometrisch
    "diff_asin": "Afgeleide van arcsin(u): d/dx[arcsin({u})] = {u'}/√(1-{u}²) → {resultaat}",
    "diff_acos": "Afgeleide van arccos(u): d/dx[arccos({u})] = -{u'}/√(1-{u}²) → {resultaat}",
    "diff_atan": "Afgeleide van arctan(u): d/dx[arctan({u})] = {u'}/(1+{u}²) → {resultaat}",
    
    # Differentiëren - Hyperbolisch
    "diff_sinh": "Afgeleide van sinh(u): d/dx[sinh({u})] = cosh({u})·u' → {resultaat}",
    "diff_cosh": "Afgeleide van cosh(u): d/dx[cosh({u})] = sinh({u})·u' → {resultaat}",
    "diff_tanh": "Afgeleide van tanh(u): d/dx[tanh({u})] = sech²({u})·u' → {resultaat}",
    
    # Integreren - Basis
    "int_power": "Pas de **machtregel voor integreren** toe: ∫{x}^{n} dx = {x}^{{n+1}}/({n+1}) + C → {resultaat}",
    "int_const": "Integraal van een constante: ∫{c} dx = {c}·x + C",
    "int_sum": "Integreer **term voor term**: ∫({a} + {b}) dx = ∫{a} dx + ∫{b} dx",
    "int_constant_factor": "Haal constante factor buiten: ∫{c}·{f} dx = {c}·∫{f} dx → {resultaat}",
    
    # Integreren - Exponentieel en Logaritmisch
    "int_exp": "Integraal van e^u: ∫e^{u} du = e^{u} + C → {resultaat}",
    "int_exp_base": "Integraal van {a}^{u}: ∫{a}^{u} du = {a}^{u}/ln({a}) + C → {resultaat}",
    "int_ln": "Integraal van 1/u: ∫1/{u} du = ln|{u}| + C → {resultaat}",
    
    # Integreren - Goniometrisch
    "int_sin": "Integraal van sin(u): ∫sin({u}) du = -cos({u}) + C → {resultaat}",
    "int_cos": "Integraal van cos(u): ∫cos({u}) du = sin({u}) + C → {resultaat}",
    "int_tan": "Integraal van tan(u): ∫tan({u}) du = -ln|cos({u})| + C → {resultaat}",
    "int_csc": "Integraal van csc(u): ∫csc({u}) du = -ln|csc({u})+cot({u})| + C → {resultaat}",
    "int_sec": "Integraal van sec(u): ∫sec({u}) du = ln|sec({u})+tan({u})| + C → {resultaat}",
    "int_cot": "Integraal van cot(u): ∫cot({u}) du = ln|sin({u})| + C → {resultaat}",
    
    # Integreren - Speciale technieken
    "int_substitution": "Gebruik **substitutie**: u = {u}, du = {du} dx → {resultaat}",
    "int_parts": "Gebruik **partiële integratie**: ∫{u} dv = {u}·{v} - ∫{v} du → {resultaat}",
    "int_trig_subst": "Gebruik **goniometrische substitutie**: {u} = {subst} → {resultaat}",
    "int_partial_fractions": "Gebruik **breuksplitsing**: {expr} = {partial} → {resultaat}",
    
    # Vereenvoudigen
    "simp_combin": "Combineer gelijksoortige termen: {a} + {b} = {resultaat}",
    "simp_trig": "Gebruik trigonometrische identiteit: {a} = {resultaat}",
    "simp_exp": "Gebruik exponentregels: {a} = {resultaat}",
    "simp_log": "Gebruik logaritme-regels: {a} = {resultaat}",
    "simp_frac": "Vereenvoudig breuk: {a} = {resultaat}",
    "simp_power": "Vereenvoudig macht: {a} = {resultaat}",
    "simp_abs": "Vereenvoudig absolute waarde: {a} = {resultaat}",
    
    # Uitbreiden
    "expand_power": "Werk macht uit: {a}^{{n}} = {resultaat}",
    "expand_product": "Werk product uit: {a}·{b} = {resultaat}",
    "expand_sum": "Werk som uit: {a} = {resultaat}",
    "expand_trig": "Gebruik goniometrische formule: {a} = {resultaat}",
    "expand_log": "Gebruik logaritme-regels: {a} = {resultaat}",
    
    # Factoriseren
    "factor_common": "Haal gemeenschappelijke factor buiten haakjes: {a} = {resultaat}",
    "factor_quad": "Factoriseer kwadratische vorm: {a} = {resultaat}",
    "factor_diff": "Gebruik verschil van kwadraten: {a} = {resultaat}",
    "factor_sum": "Gebruik som van kwadraten: {a} = {resultaat}",
    "factor_cubic": "Factoriseer derdegraads vorm: {a} = {resultaat}",
    "factor_trig": "Factoriseer trigonometrische uitdrukking: {a} = {resultaat}",
    "factor_group": "Groepeer termen: {a} = {resultaat}",
    
    # Limieten
    "lim_direct": "Direct invullen: lim_{{{var}→{waarde}}} {expr} = {resultaat}",
    "lim_frac": "Vereenvoudig breuk: {expr} = {resultaat}",
    "lim_fact": "Factoriseer om {waarde} te vermijden: {expr} = {resultaat}",
    "lim_lhopital": "Gebruik **l'Hôpital**: lim_{{{var}→{waarde}}} {expr} = lim_{{{var}→{waarde}}} {gen} → {resultaat}",
    "lim_special": "Gebruik speciale limiet: {expr} = {resultaat}",
    "lim_squeeze": "Gebruik **insluitingsstelling**: {a} ≤ {expr} ≤ {b} → {resultaat}",
    
    # Taylor
    "taylor_term": "Term {k}: {label} = {resultaat}",
    "taylor_series": "Taylorreeks: {series}",
    
    # Oplossen
    "solve_linear": "Lineaire vergelijking: {a}x + {b} = 0 → x = -{b}/{a}",
    "solve_quadratic": "Kwadratische vergelijking: {a}x² + {b}x + {c} = 0 → x = {solution}",
    "solve_absolute": "Absolute waarde oplossen: |{expr}| = {waarde} → {solution}",
    "solve_rational": "Rationale vergelijking: {expr} → {solution}",
}

# --------------------------------------------
# CAS FUNCTIES (Snel)
# --------------------------------------------
def doe_diff(s):
    return pretty(sp.diff(trig_fix(expr(s))))

def doe_simpel(s):
    return pretty(sp.simplify(trig_fix(expr(s))))

def doe_expand(s):
    return pretty(sp.expand(trig_fix(expr(s))))

def doe_factor(s):
    return pretty(sp.factor(trig_fix(expr(s))))

def doe_int(s):
    return pretty(sp.integrate(trig_fix(expr(s))))

def doe_limiet(e, v, r):
    try:
        return pretty(sp.limit(expr(e), symbols[v], expr(r)))
    except:
        return "Kan limiet niet berekenen."

def doe_oplossen(s):
    s = s.strip()
    try:
        if "voor" in s:
            eq, var = s.split("voor", 1)
            var = var.strip()
            eq = eq.replace("op", "").strip()
            if "=" in eq:
                L, R = eq.split("=", 1)
                sol = sp.solve(sp.Eq(expr(L), expr(R)), symbols[var])
            else:
                sol = sp.solve(expr(eq), symbols[var])
        else:
            if "=" in s:
                L, R = s.split("=", 1)
                sol = sp.solve(sp.Eq(expr(L), expr(R)))
            else:
                sol = sp.solve(sp.Eq(expr(s), 0))
        
        if not sol:
            return "Geen oplossing gevonden."
        return ", ".join(pretty(v) for v in sol)
    except Exception as e:
        return f"Fout bij oplossen: {e}"

def doe_pyth(z):
    parts = z.split()[1:]
    waarden = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            try:
                waarden[k] = expr(v)
            except:
                return "Ongeldige waarde voor {k}".format(k=k)
    
    a = waarden.get("a", None)
    b = waarden.get("b", None)
    c = waarden.get("c", None)
    
    try:
        if a is None and b is not None and c is not None:
            result = sp.sqrt(c**2 - b**2)
            return pretty(result)
        if b is None and a is not None and c is not None:
            result = sp.sqrt(c**2 - a**2)
            return pretty(result)
        if c is None and a is not None and b is not None:
            result = sp.sqrt(a**2 + b**2)
            return pretty(result)
    except:
        return "Kan Pythagoras niet berekenen."
    
    return "Gebruik: pyth a=... b=... c=..."
# ============================================
#   SemCAS 11.1 — Blok 2: Differentiëren met Stappen (Uitgebreid)
# ============================================

def doe_diff_met_stappen(s):
    stap = StapGenerator()
    try:
        f = trig_fix(expr(s))
        x = sp.Symbol('x')
        stap.voeg_stap_toe("Start met: f(x) = {f}", f=f)
        stap.voeg_stap_toe("We gaan differentiëren naar x.")
        stap.voeg_stap_toe("")
        
        resultaat = _genereer_diff(f, x, stap)
        
        if resultaat is None:
            resultaat = sp.diff(f, x)
        
        stap.voeg_stap_toe("")
        stap.voeg_stap_toe("✅ **Eindresultaat:** f'(x) = {resultaat}", resultaat=sp.simplify(resultaat))
        
        return stap.toon_stappen("📐 **Differentiëren - Stap-voor-stap**")
    except Exception as e:
        return f"Fout bij differentiëren: {e}"

def _genereer_diff(expr, var, stap):
    """Genereer stappen voor differentiëren - Uitgebreide versie"""
    
    # Constante
    if expr.is_Number:
        stap.voeg_stap_toe(TEMPLATES["diff_const"], c=expr)
        return 0
    
    # Variabele
    if expr.is_Symbol:
        if expr == var:
            stap.voeg_stap_toe(TEMPLATES["diff_power"], x=var, n=1, resultaat=1)
            return 1
        elif str(expr).islower():
            stap.voeg_stap_toe(TEMPLATES["diff_const"], c=expr)
            return 0
        else:
            stap.voeg_stap_toe("Differentieer variabele: d/dx[{expr}] = {resultaat}", expr=expr, resultaat=0)
            return 0
    
    # Macht: x^n of f(x)^n
    if isinstance(expr, sp.Pow):
        base, exp = expr.args
        
        # Simpele macht: x^n
        if base == var:
            resultaat = exp * var**(exp-1)
            stap.voeg_stap_toe(TEMPLATES["diff_power"], x=var, n=exp, resultaat=resultaat)
            return resultaat
        
        # Constante macht: c^n
        if base.is_Number:
            resultaat = 0
            stap.voeg_stap_toe(TEMPLATES["diff_const"], c=expr)
            return resultaat
        
        # Kettingregel voor macht: f(x)^n
        stap.voeg_stap_toe(TEMPLATES["diff_chain_power"], base=base, exp=exp)
        stap.verdiep()
        base_prime = _genereer_diff(base, var, stap)
        stap.verdiep_uit()
        resultaat = exp * base**(exp-1) * base_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Som
    if expr.is_Add:
        stap.voeg_stap_toe(TEMPLATES["diff_sum"], a=expr.args[0], b=expr.args[1:])
        resultaat = 0
        stap.verdiep()
        for arg in expr.args:
            resultaat += _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        return resultaat
    
    # Product
    if expr.is_Mul:
        if len(expr.args) == 2:
            f, g = expr.args
            
            # Check of het een constante keer een functie is
            if f.is_Number:
                stap.voeg_stap_toe("Neem constante factor {c} buiten: {c}·d/dx[{g}]", c=f, g=g)
                stap.verdiep()
                g_prime = _genereer_diff(g, var, stap)
                stap.verdiep_uit()
                resultaat = f * g_prime
                stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
                return resultaat
            
            if g.is_Number:
                stap.voeg_stap_toe("Neem constante factor {c} buiten: {c}·d/dx[{f}]", c=g, f=f)
                stap.verdiep()
                f_prime = _genereer_diff(f, var, stap)
                stap.verdiep_uit()
                resultaat = g * f_prime
                stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
                return resultaat
            
            # Productregel
            stap.voeg_stap_toe(TEMPLATES["diff_product"], f=f, g=g)
            stap.verdiep()
            f_prime = _genereer_diff(f, var, stap)
            g_prime = _genereer_diff(g, var, stap)
            stap.verdiep_uit()
            resultaat = f_prime * g + f * g_prime
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
        else:
            # Meer dan 2 factoren
            stap.voeg_stap_toe("Pas **productregel** toe op meerdere factoren")
            resultaat = 0
            stap.verdiep()
            for i, arg in enumerate(expr.args):
                rest = sp.Mul(*[expr.args[j] for j in range(len(expr.args)) if j != i])
                arg_prime = _genereer_diff(arg, var, stap)
                resultaat += arg_prime * rest
            stap.verdiep_uit()
            return resultaat
    
    # Quotiënt
    if expr.is_Mul and any(isinstance(arg, sp.Pow) and arg.args[1] < 0 for arg in expr.args):
        # Herken als quotiënt
        teller = sp.numer(expr)
        noemer = sp.denom(expr)
        if teller != expr:
            stap.voeg_stap_toe(TEMPLATES["diff_quotient"], f=teller, g=noemer)
            stap.verdiep()
            f_prime = _genereer_diff(teller, var, stap)
            g_prime = _genereer_diff(noemer, var, stap)
            stap.verdiep_uit()
            resultaat = (f_prime * noemer - teller * g_prime) / (noemer**2)
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
    
    # Exponentieel: e^u
    if expr.func == sp.exp:
        arg = expr.args[0]
        if arg == var:
            stap.voeg_stap_toe(TEMPLATES["diff_exp"], u=var, resultaat=expr)
            return expr
        stap.voeg_stap_toe(TEMPLATES["diff_exp"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = expr * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Logaritme: ln(u)
    if expr.func == sp.log:
        arg = expr.args[0]
        if arg == var:
            stap.voeg_stap_toe(TEMPLATES["diff_ln"], u=var, resultaat=1/var)
            return 1/var
        stap.voeg_stap_toe(TEMPLATES["diff_ln"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = arg_prime / arg
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Sinus
    if expr.func == sp.sin:
        arg = expr.args[0]
        if arg == var:
            stap.voeg_stap_toe(TEMPLATES["diff_sin"], u=var, resultaat=sp.cos(var))
            return sp.cos(var)
        stap.voeg_stap_toe(TEMPLATES["diff_sin"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = sp.cos(arg) * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Cosinus
    if expr.func == sp.cos:
        arg = expr.args[0]
        if arg == var:
            stap.voeg_stap_toe(TEMPLATES["diff_cos"], u=var, resultaat=-sp.sin(var))
            return -sp.sin(var)
        stap.voeg_stap_toe(TEMPLATES["diff_cos"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = -sp.sin(arg) * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Tangens
    if expr.func == sp.tan:
        arg = expr.args[0]
        if arg == var:
            stap.voeg_stap_toe(TEMPLATES["diff_tan"], u=var, resultaat=1+sp.tan(var)**2)
            return 1+sp.tan(var)**2
        stap.voeg_stap_toe(TEMPLATES["diff_tan"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = (1 + sp.tan(arg)**2) * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Csc
    if expr.func == sp.csc:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["diff_csc"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = -sp.csc(arg) * sp.cot(arg) * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Sec
    if expr.func == sp.sec:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["diff_sec"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = sp.sec(arg) * sp.tan(arg) * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Cot
    if expr.func == sp.cot:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["diff_cot"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = -sp.csc(arg)**2 * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Arcsin
    if expr.func == sp.asin:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["diff_asin"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = arg_prime / sp.sqrt(1 - arg**2)
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Arccos
    if expr.func == sp.acos:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["diff_acos"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = -arg_prime / sp.sqrt(1 - arg**2)
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Arctan
    if expr.func == sp.atan:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["diff_atan"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = arg_prime / (1 + arg**2)
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Sinh
    if expr.func == sp.sinh:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["diff_sinh"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = sp.cosh(arg) * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Cosh
    if expr.func == sp.cosh:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["diff_cosh"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = sp.sinh(arg) * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Tanh
    if expr.func == sp.tanh:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["diff_tanh"], u=arg)
        stap.verdiep()
        arg_prime = _genereer_diff(arg, var, stap)
        stap.verdiep_uit()
        resultaat = (1 - sp.tanh(arg)**2) * arg_prime
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Fallback
    try:
        resultaat = sp.diff(expr, var)
        if resultaat != expr:
            stap.voeg_stap_toe("Differentieer: d/dx[{expr}] = {resultaat}", expr=expr, resultaat=resultaat)
            return resultaat
    except:
        pass
    
    stap.voeg_stap_toe("⚠️ Kan {expr} niet differentiëren met standaardregels.", expr=expr)
    return None
# ============================================
#   SemCAS 11.1 — Blok 3: Integreren met Stappen (Uitgebreid)
# ============================================

def doe_int_met_stappen(s):
    stap = StapGenerator()
    try:
        f = trig_fix(expr(s))
        x = sp.Symbol('x')
        stap.voeg_stap_toe("Start met: f(x) = {f}", f=f)
        stap.voeg_stap_toe("We gaan integreren naar x.")
        stap.voeg_stap_toe("")
        
        resultaat = _genereer_int(f, x, stap)
        
        if resultaat is None:
            resultaat = sp.integrate(f, x)
        
        stap.voeg_stap_toe("")
        stap.voeg_stap_toe("✅ **Eindresultaat:** ∫f(x) dx = {resultaat} + C", resultaat=sp.simplify(resultaat))
        
        return stap.toon_stappen("📐 **Integreren - Stap-voor-stap**")
    except Exception as e:
        return f"Fout bij integreren: {e}"

def _genereer_int(expr, var, stap):
    """Genereer stappen voor integreren - Uitgebreide versie"""
    
    # Constante
    if expr.is_Number:
        stap.voeg_stap_toe(TEMPLATES["int_const"], c=expr)
        return expr * var
    
    # Variabele
    if expr.is_Symbol:
        if expr == var:
            stap.voeg_stap_toe(TEMPLATES["int_power"], x=var, n=1, resultaat=var**2/2)
            return var**2/2
        else:
            stap.voeg_stap_toe("Integreer naar x: ∫{expr} dx = {expr}·x + C", expr=expr)
            return expr * var
    
    # Macht: x^n
    if isinstance(expr, sp.Pow):
        base, exp = expr.args
        if base == var:
            if exp != -1:
                resultaat = var**(exp+1)/(exp+1)
                stap.voeg_stap_toe(TEMPLATES["int_power"], x=var, n=exp, resultaat=resultaat)
                return resultaat
            else:
                resultaat = sp.log(var)
                stap.voeg_stap_toe(TEMPLATES["int_ln"], u=var, resultaat=resultaat)
                return resultaat
        elif exp == -1:
            # 1/(ax+b) vorm
            stap.voeg_stap_toe(TEMPLATES["int_ln"], u=base)
            stap.verdiep()
            resultaat = sp.log(base) / sp.diff(base, var)
            stap.verdiep_uit()
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
        else:
            # (ax+b)^n met n ≠ -1
            stap.voeg_stap_toe("Gebruik substitutie voor ∫{base}^{exp} dx", base=base, exp=exp)
            stap.verdiep()
            stap.voeg_stap_toe("Stel u = {base}, dan du = {diff} dx", base=base, diff=sp.diff(base, var))
            resultaat = (base**(exp+1)) / ((exp+1) * sp.diff(base, var))
            stap.verdiep_uit()
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
    
    # Som
    if expr.is_Add:
        stap.voeg_stap_toe(TEMPLATES["int_sum"], a=expr.args[0], b=expr.args[1:])
        resultaat = 0
        stap.verdiep()
        for arg in expr.args:
            resultaat += _genereer_int(arg, var, stap)
        stap.verdiep_uit()
        return resultaat
    
    # Constante factor
    if expr.is_Mul and len(expr.args) == 2:
        f, g = expr.args
        
        # Constante * functie
        if f.is_Number:
            stap.voeg_stap_toe(TEMPLATES["int_constant_factor"], c=f, f=g)
            stap.verdiep()
            g_int = _genereer_int(g, var, stap)
            stap.verdiep_uit()
            resultaat = f * g_int
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
        
        if g.is_Number:
            stap.voeg_stap_toe(TEMPLATES["int_constant_factor"], c=g, f=f)
            stap.verdiep()
            f_int = _genereer_int(f, var, stap)
            stap.verdiep_uit()
            resultaat = g * f_int
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
        
        # Kettingregel: f(g(x)) * g'(x)
        if f.func in (sp.sin, sp.cos, sp.exp, sp.log, sp.tan, sp.csc, sp.sec, sp.cot):
            if len(f.args) == 1:
                inner = f.args[0]
                inner_diff = sp.diff(inner, var)
                if inner_diff == g or inner_diff == g * sp.Integer(1):
                    stap.voeg_stap_toe("Herken **kettingregel**: ∫{f}({inner})·{g} dx", 
                                      f=f.func.__name__, inner=inner, g=g)
                    stap.verdiep()
                    stap.voeg_stap_toe("Stel u = {inner}, dan du = {g} dx", inner=inner, g=g)
                    resultaat = sp.integrate(f, inner)
                    stap.verdiep_uit()
                    stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
                    return resultaat
    
    # Exponentieel: e^u
    if expr.func == sp.exp:
        arg = expr.args[0]
        if arg == var:
            stap.voeg_stap_toe(TEMPLATES["int_exp"], u=var, resultaat=expr)
            return expr
        else:
            stap.voeg_stap_toe(TEMPLATES["int_exp"], u=arg)
            stap.verdiep()
            resultaat = expr / sp.diff(arg, var)
            stap.verdiep_uit()
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
    
    # Logaritme: ln(u)
    if expr.func == sp.log:
        arg = expr.args[0]
        if arg == var:
            # ∫ln(x) dx = x·ln(x) - x
            resultaat = var * sp.log(var) - var
            stap.voeg_stap_toe("Gebruik partiële integratie voor ∫ln({u}) du = {u}·ln({u}) - {u} + C", 
                              u=var, resultaat=resultaat)
            return resultaat
        else:
            # ∫ln(ax+b) dx
            stap.voeg_stap_toe("Gebruik substitutie voor ∫ln({arg}) dx", arg=arg)
            stap.verdiep()
            stap.voeg_stap_toe("Stel u = {arg}, dan du = {diff} dx", arg=arg, diff=sp.diff(arg, var))
            resultaat = (arg * sp.log(arg) - arg) / sp.diff(arg, var)
            stap.verdiep_uit()
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
    
    # Sinus
    if expr.func == sp.sin:
        arg = expr.args[0]
        if arg == var:
            stap.voeg_stap_toe(TEMPLATES["int_sin"], u=var, resultaat=-sp.cos(var))
            return -sp.cos(var)
        else:
            stap.voeg_stap_toe(TEMPLATES["int_sin"], u=arg)
            stap.verdiep()
            resultaat = -sp.cos(arg) / sp.diff(arg, var)
            stap.verdiep_uit()
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
    
    # Cosinus
    if expr.func == sp.cos:
        arg = expr.args[0]
        if arg == var:
            stap.voeg_stap_toe(TEMPLATES["int_cos"], u=var, resultaat=sp.sin(var))
            return sp.sin(var)
        else:
            stap.voeg_stap_toe(TEMPLATES["int_cos"], u=arg)
            stap.verdiep()
            resultaat = sp.sin(arg) / sp.diff(arg, var)
            stap.verdiep_uit()
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
    
    # Tangens
    if expr.func == sp.tan:
        arg = expr.args[0]
        if arg == var:
            stap.voeg_stap_toe(TEMPLATES["int_tan"], u=var, resultaat=-sp.log(sp.cos(var)))
            return -sp.log(sp.cos(var))
        else:
            stap.voeg_stap_toe(TEMPLATES["int_tan"], u=arg)
            stap.verdiep()
            resultaat = -sp.log(sp.cos(arg)) / sp.diff(arg, var)
            stap.verdiep_uit()
            stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
            return resultaat
    
    # Csc
    if expr.func == sp.csc:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["int_csc"], u=arg)
        stap.verdiep()
        resultaat = -sp.log(sp.csc(arg) + sp.cot(arg)) / sp.diff(arg, var)
        stap.verdiep_uit()
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Sec
    if expr.func == sp.sec:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["int_sec"], u=arg)
        stap.verdiep()
        resultaat = sp.log(sp.sec(arg) + sp.tan(arg)) / sp.diff(arg, var)
        stap.verdiep_uit()
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Cot
    if expr.func == sp.cot:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["int_cot"], u=arg)
        stap.verdiep()
        resultaat = sp.log(sp.sin(arg)) / sp.diff(arg, var)
        stap.verdiep_uit()
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Sinh
    if expr.func == sp.sinh:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["int_exp"], u=arg)
        stap.verdiep()
        resultaat = sp.cosh(arg) / sp.diff(arg, var)
        stap.verdiep_uit()
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Cosh
    if expr.func == sp.cosh:
        arg = expr.args[0]
        stap.voeg_stap_toe(TEMPLATES["int_exp"], u=arg)
        stap.verdiep()
        resultaat = sp.sinh(arg) / sp.diff(arg, var)
        stap.verdiep_uit()
        stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
        return resultaat
    
    # Breuk: probeer breuksplitsing
    if expr.is_Mul or isinstance(expr, sp.Pow):
        teller = sp.numer(expr)
        noemer = sp.denom(expr)
        if noemer != 1 and teller != expr:
            # Probeer breuksplitsing
            try:
                partial = sp.apart(expr, var)
                if partial != expr:
                    stap.voeg_stap_toe(TEMPLATES["int_partial_fractions"], expr=expr, partial=partial)
                    stap.verdiep()
                    resultaat = _genereer_int(partial, var, stap)
                    stap.verdiep_uit()
                    return resultaat
            except:
                pass
    
    # Fallback: probeer gewoon te integreren
    try:
        resultaat = sp.integrate(expr, var)
        if resultaat != expr * var and resultaat is not None:
            stap.voeg_stap_toe("Integreer: ∫{expr} dx = {resultaat}", expr=expr, resultaat=resultaat)
            return resultaat
    except:
        pass
    
    # Partiële integratie
    if expr.is_Mul and len(expr.args) == 2:
        stap.voeg_stap_toe("Probeer **partiële integratie** voor ∫{expr} dx", expr=expr)
        u = expr.args[0]
        dv = expr.args[1]
        try:
            v = sp.integrate(dv, var)
            du = sp.diff(u, var)
            stap.voeg_stap_toe(TEMPLATES["int_parts"], u=u, v=v)
            stap.verdiep()
            resultaat = u * v - sp.integrate(v * du, var)
            stap.verdiep_uit()
            if resultaat != expr:
                stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
                return resultaat
        except:
            pass
        
        # Probeer andersom
        stap.voeg_stap_toe("Probeer partiële integratie met u = {u}, dv = {dv}", u=dv, dv=u)
        try:
            v = sp.integrate(u, var)
            du = sp.diff(dv, var)
            stap.voeg_stap_toe(TEMPLATES["int_parts"], u=dv, v=v)
            stap.verdiep()
            resultaat = dv * v - sp.integrate(v * du, var)
            stap.verdiep_uit()
            if resultaat != expr:
                stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
                return resultaat
        except:
            pass
    
    stap.voeg_stap_toe("⚠️ Kan {expr} niet integreren met standaardregels.", expr=expr)
    return None
# ============================================
#   SemCAS 11.1 — Blok 4: Limieten + Vereenvoudigen + Uitbreiden + Factoriseren
# ============================================

def doe_limiet_met_stappen(e, v, r):
    stap = StapGenerator()
    try:
        x = sp.Symbol('x')
        f = expr(e)
        a = expr(r)
        
        stap.voeg_stap_toe("Start met: lim_{{{var}→{waarde}}} {expr}", var=v, waarde=a, expr=f)
        stap.voeg_stap_toe("")
        
        # Stap 1: Probeer direct in te vullen
        try:
            direct = f.subs(x, a)
            if not any(t in str(direct) for t in ['zoo', 'nan', 'Infinity', 'NegativeInfinity']):
                stap.voeg_stap_toe(TEMPLATES["lim_direct"], var=v, waarde=a, expr=f, resultaat=direct)
                resultaat = direct
            else:
                # Stap 2: Vereenvoudig eerst
                vereenvoudigd = sp.simplify(f)
                if vereenvoudigd != f:
                    stap.voeg_stap_toe(TEMPLATES["lim_frac"], expr=f, resultaat=vereenvoudigd)
                    f = vereenvoudigd
                
                # Stap 3: Probeer te factoriseren
                gefactoriseerd = sp.factor(f)
                if gefactoriseerd != f:
                    stap.voeg_stap_toe(TEMPLATES["lim_fact"], expr=f, waarde=a, gefactoriseerd=gefactoriseerd)
                    f = gefactoriseerd
                
                # Stap 4: Check of we l'Hôpital kunnen gebruiken
                teller = sp.numer(f)
                noemer = sp.denom(f)
                teller_waarde = teller.subs(x, a)
                noemer_waarde = noemer.subs(x, a)
                
                if teller_waarde == 0 and noemer_waarde == 0:
                    stap.voeg_stap_toe("We hebben 0/0 → gebruik **l'Hôpital**")
                    stap.verdiep()
                    stap.voeg_stap_toe("Differentieer teller en noemer apart:")
                    
                    teller_afg = sp.diff(teller, x)
                    noemer_afg = sp.diff(noemer, x)
                    
                    stap.voeg_stap_toe("  d/dx[{teller}] = {teller_afg}", teller=teller, teller_afg=teller_afg)
                    stap.voeg_stap_toe("  d/dx[{noemer}] = {noemer_afg}", noemer=noemer, noemer_afg=noemer_afg)
                    
                    nieuwe_breuk = teller_afg / noemer_afg
                    stap.voeg_stap_toe(TEMPLATES["lim_lhopital"], var=v, waarde=a, expr=f, gen=nieuwe_breuk)
                    
                    resultaat = sp.limit(nieuwe_breuk, x, a)
                    stap.voeg_stap_toe("   = {resultaat}", resultaat=resultaat)
                    stap.verdiep_uit()
                else:
                    resultaat = sp.limit(f, x, a)
                    stap.voeg_stap_toe(TEMPLATES["lim_direct"], var=v, waarde=a, expr=f, resultaat=resultaat)
        except:
            resultaat = sp.limit(f, x, a)
            stap.voeg_stap_toe(TEMPLATES["lim_direct"], var=v, waarde=a, expr=f, resultaat=resultaat)
        
        stap.voeg_stap_toe("")
        stap.voeg_stap_toe("✅ **Eindresultaat:** lim_{{{var}→{waarde}}} {expr} = {resultaat}", 
                          var=v, waarde=a, expr=f, resultaat=resultaat)
        
        return stap.toon_stappen("📐 **Limiet - Stap-voor-stap**")
    except Exception as e:
        return f"Fout bij limiet: {e}"

# --------------------------------------------
# Vereenvoudigen met Stappen - Uitgebreid
# --------------------------------------------
def doe_simpel_met_stappen(s):
    stap = StapGenerator()
    try:
        f = trig_fix(expr(s))
        stap.voeg_stap_toe("Start met: {expr}", expr=f)
        stap.voeg_stap_toe("We gaan vereenvoudigen.")
        stap.voeg_stap_toe("")
        
        huidig = f
        stappen_gezet = False
        
        # Stap 1: Vereenvoudig breuken
        vereenvoudigd = sp.simplify(huidig)
        if vereenvoudigd != huidig:
            stap.voeg_stap_toe(TEMPLATES["simp_frac"], a=huidig, resultaat=vereenvoudigd)
            huidig = vereenvoudigd
            stappen_gezet = True
        
        # Stap 2: Combineer gelijksoortige termen
        if huidig.is_Add:
            gecombineerd = sp.collect(huidig, sp.Symbol('x'))
            if gecombineerd != huidig:
                stap.voeg_stap_toe(TEMPLATES["simp_combin"], a=huidig, b="", resultaat=gecombineerd)
                huidig = gecombineerd
                stappen_gezet = True
        
        # Stap 3: Trig vereenvoudiging
        trigsimp = sp.trigsimp(huidig)
        if trigsimp != huidig:
            stap.voeg_stap_toe(TEMPLATES["simp_trig"], a=huidig, resultaat=trigsimp)
            huidig = trigsimp
            stappen_gezet = True
        
        # Stap 4: Exponentiële vereenvoudiging
        expsimp = sp.powsimp(huidig)
        if expsimp != huidig:
            stap.voeg_stap_toe(TEMPLATES["simp_exp"], a=huidig, resultaat=expsimp)
            huidig = expsimp
            stappen_gezet = True
        
        # Stap 5: Log vereenvoudiging
        logsimp = sp.logcombine(huidig)
        if logsimp != huidig:
            stap.voeg_stap_toe(TEMPLATES["simp_log"], a=huidig, resultaat=logsimp)
            huidig = logsimp
            stappen_gezet = True
        
        if not stappen_gezet:
            stap.voeg_stap_toe("Uitdrukking is al in de meest eenvoudige vorm.")
        
        stap.voeg_stap_toe("")
        stap.voeg_stap_toe("✅ **Eindresultaat:** {resultaat}", resultaat=huidig)
        
        return stap.toon_stappen("📐 **Vereenvoudigen - Stap-voor-stap**")
    except Exception as e:
        return f"Fout bij vereenvoudigen: {e}"

# --------------------------------------------
# Uitbreiden met Stappen - Uitgebreid
# --------------------------------------------
def doe_expand_met_stappen(s):
    stap = StapGenerator()
    try:
        f = trig_fix(expr(s))
        stap.voeg_stap_toe("Start met: {expr}", expr=f)
        stap.voeg_stap_toe("We gaan uitbreiden.")
        stap.voeg_stap_toe("")
        
        huidig = f
        stappen_gezet = False
        
        # Stap 1: Werk machten uit
        if isinstance(huidig, sp.Pow):
            base, exp = huidig.args
            stap.voeg_stap_toe(TEMPLATES["expand_power"], a=base, n=exp)
        
        uitgebreid = sp.expand(huidig)
        if uitgebreid != huidig:
            if not isinstance(huidig, sp.Pow):
                stap.voeg_stap_toe(TEMPLATES["expand_product"], a=huidig, resultaat=uitgebreid)
            huidig = uitgebreid
            stappen_gezet = True
        
        # Stap 2: Trig uitbreiding
        trige = sp.expand_trig(huidig)
        if trige != huidig:
            stap.voeg_stap_toe(TEMPLATES["expand_trig"], a=huidig, resultaat=trige)
            huidig = trige
            stappen_gezet = True
        
        # Stap 3: Log uitbreiding
        logexp = sp.expand_log(huidig)
        if logexp != huidig:
            stap.voeg_stap_toe(TEMPLATES["expand_log"], a=huidig, resultaat=logexp)
            huidig = logexp
            stappen_gezet = True
        
        if not stappen_gezet:
            stap.voeg_stap_toe("Uitdrukking is al volledig uitgebreid.")
        
        stap.voeg_stap_toe("")
        stap.voeg_stap_toe("✅ **Eindresultaat:** {resultaat}", resultaat=huidig)
        
        return stap.toon_stappen("📐 **Uitbreiden - Stap-voor-stap**")
    except Exception as e:
        return f"Fout bij uitbreiden: {e}"

# --------------------------------------------
# Factoriseren met Stappen - Uitgebreid
# --------------------------------------------
def doe_factor_met_stappen(s):
    stap = StapGenerator()
    try:
        f = trig_fix(expr(s))
        stap.voeg_stap_toe("Start met: {expr}", expr=f)
        stap.voeg_stap_toe("We gaan factoriseren.")
        stap.voeg_stap_toe("")
        
        huidig = f
        stappen_gezet = False
        
        # Stap 1: Haal gemeenschappelijke factor buiten
        gefactoriseerd = sp.factor(huidig)
        if gefactoriseerd != huidig:
            if isinstance(gefactoriseerd, sp.Mul):
                stap.voeg_stap_toe(TEMPLATES["factor_common"], a=huidig, resultaat=gefactoriseerd)
            elif isinstance(gefactoriseerd, sp.Pow):
                stap.voeg_stap_toe(TEMPLATES["factor_diff"], a=huidig, resultaat=gefactoriseerd)
            else:
                stap.voeg_stap_toe(TEMPLATES["factor_quad"], a=huidig, resultaat=gefactoriseerd)
            huidig = gefactoriseerd
            stappen_gezet = True
        
        # Stap 2: Groepeer termen
        if huidig.is_Add and len(huidig.args) >= 4:
            try:
                gegroepeerd = sp.factor(huidig, deep=True)
                if gegroepeerd != huidig:
                    stap.voeg_stap_toe(TEMPLATES["factor_group"], a=huidig, resultaat=gegroepeerd)
                    huidig = gegroepeerd
                    stappen_gezet = True
            except:
                pass
        
        if not stappen_gezet:
            stap.voeg_stap_toe("Uitdrukking is al volledig gefactoriseerd.")
        
        stap.voeg_stap_toe("")
        stap.voeg_stap_toe("✅ **Eindresultaat:** {resultaat}", resultaat=huidig)
        
        return stap.toon_stappen("📐 **Factoriseren - Stap-voor-stap**")
    except Exception as e:
        return f"Fout bij factoriseren: {e}"
# ============================================
#   SemCAS 11.1 — Blok 5: Kwadratisch + Taylor + Oplosser + Parser + REPL
# ============================================

# --------------------------------------------
# OPLOSSEN MET STAPPEN - ALGEMEEN (MET ALLE STAPPEN)
# --------------------------------------------
def los_op_met_stappen(vergelijking):
    """
    Los vergelijkingen op met stap-voor-stap uitleg
    Ondersteunt: lineair, kwadratisch, hogere machten, 
                 absolute waarde, rationale vergelijkingen
    """
    stappen = []
    try:
        # Parse de vergelijking
        if "=" in vergelijking:
            links, rechts = vergelijking.split("=", 1)
            links_expr = expr(links.strip())
            rechts_expr = expr(rechts.strip())
            verg = links_expr - rechts_expr
        else:
            verg = expr(vergelijking)
        
        x = sp.Symbol('x')
        
        stappen.append("📐 **Stap 1:** Schrijf de vergelijking in standaardvorm")
        if "=" in vergelijking:
            stappen.append(f"   {pretty(links_expr)} = {pretty(rechts_expr)}")
            stappen.append(f"   → {pretty(verg)} = 0")
        else:
            stappen.append(f"   {pretty(verg)} = 0")
        stappen.append("")
        
        # Stap 2: Vereenvoudig (altijd tonen)
        stappen.append("🔧 **Stap 2:** Vereenvoudig de uitdrukking")
        vereenvoudigd = sp.simplify(verg)
        if vereenvoudigd != verg:
            stappen.append(f"   {pretty(verg)} = {pretty(vereenvoudigd)}")
            verg = vereenvoudigd
        else:
            stappen.append(f"   {pretty(verg)} is al in de meest eenvoudige vorm.")
        stappen.append("")
        
        # Stap 3: Probeer te factoriseren (altijd tonen)
        stappen.append("🔧 **Stap 3:** Probeer te factoriseren")
        gefactoriseerd = sp.factor(verg)
        if gefactoriseerd != verg and gefactoriseerd is not None:
            stappen.append(f"   {pretty(verg)} = {pretty(gefactoriseerd)}")
            verg = gefactoriseerd
        else:
            stappen.append(f"   {pretty(verg)} kan niet verder worden gefactoriseerd.")
        stappen.append("")
        
        # Stap 4: Los op
        stappen.append("🔢 **Stap 4:** Los op")
        
        try:
            oplossingen = sp.solve(verg, x)
        except:
            oplossingen = []
        
        if not oplossingen:
            return "Geen oplossingen gevonden."
        
        if len(oplossingen) == 1:
            stappen.append(f"   x = {pretty(oplossingen[0])}")
        else:
            stappen.append(f"   x = {', '.join(pretty(v) for v in oplossingen)}")
        
        stappen.append("")
        
        # Stap 5: Controleer
        stappen.append("✅ **Stap 5:** Controleer de oplossingen")
        for i, sol in enumerate(oplossingen, 1):
            try:
                check = sp.simplify(verg.subs(x, sol))
                if check == 0:
                    stappen.append(f"   x = {pretty(sol)}: {pretty(verg)} = 0 ✓")
                else:
                    stappen.append(f"   x = {pretty(sol)}: {pretty(verg)} = {pretty(check)}")
            except:
                pass
        
        stappen.append("")
        stappen.append(f"✅ **Oplossing:** {', '.join(pretty(v) for v in oplossingen)}")
        
        return "\n".join(stappen)
        
    except Exception as e:
        return f"Fout bij oplossen: {e}"

# --------------------------------------------
# KWADRATISCHE OPLOSSER (speciaal geval - alle stappen)
# --------------------------------------------
def los_kwadratisch_op_met_stappen(vergelijking):
    stappen = []
    try:
        if "=" in vergelijking:
            links, rechts = vergelijking.split("=", 1)
            verg = expr(links.strip()) - expr(rechts.strip())
        else:
            verg = expr(vergelijking)
        
        x = sp.Symbol('x')
        verg = sp.simplify(verg)
        
        stappen.append("📐 **Stap 1:** Herken de kwadratische vorm")
        stappen.append(f"   {pretty(verg)} = 0")
        stappen.append("")
        
        poly = sp.Poly(verg, x)
        coeffs = poly.all_coeffs()
        
        if len(coeffs) == 3:
            a, b, c = coeffs
            if a < 0:
                a, b, c = -a, -b, -c
                verg = -verg
            
            a_p, b_p, c_p = pretty(a), pretty(b), pretty(c)
            b_neg = pretty(-b)
            
            stappen.append(f"   Dus: a = {a_p}, b = {b_p}, c = {c_p}")
            stappen.append("")
            
            # Stap 2: Bereken discriminant
            D = b**2 - 4*a*c
            D_p = pretty(D)
            
            stappen.append("🔢 **Stap 2:** Bereken de discriminant")
            stappen.append("   D = b² - 4ac")
            stappen.append(f"   D = ({b_p})² - 4·({a_p})·({c_p})")
            stappen.append(f"   D = {pretty(b**2)} - {pretty(4*a*c)}")
            stappen.append(f"   D = {D_p}")
            stappen.append("")
            
            # Stap 3: Bepaal aantal oplossingen
            if D > 0:
                stappen.append("✅ **Stap 3:** D > 0 → twee reële oplossingen")
                stappen.append("   Gebruik de abc-formule: x = [-b ± √D] / (2a)")
                
                x1 = (-b - sp.sqrt(D)) / (2*a)
                x2 = (-b + sp.sqrt(D)) / (2*a)
                x1_p, x2_p = pretty(sp.simplify(x1)), pretty(sp.simplify(x2))
                
                stappen.append("")
                stappen.append("📝 **Stap 4:** Bereken x₁ en x₂")
                stappen.append(f"   x₁ = [{b_neg} - √{D_p}] / (2·{a_p}) = {x1_p}")
                stappen.append(f"   x₂ = [{b_neg} + √{D_p}] / (2·{a_p}) = {x2_p}")
                stappen.append("")
                stappen.append(f"✅ **Oplossing:** x = {x1_p} of x = {x2_p}")
                
            elif D == 0:
                stappen.append("✅ **Stap 3:** D = 0 → één oplossing (dubbel)")
                x0 = -b / (2*a)
                x0_p = pretty(sp.simplify(x0))
                stappen.append(f"   x = -b / (2a) = {b_neg} / (2·{a_p}) = {x0_p}")
                stappen.append("")
                stappen.append(f"✅ **Oplossing:** x = {x0_p}")
                
            else:
                stappen.append("✅ **Stap 3:** D < 0 → twee complexe oplossingen")
                stappen.append("   Gebruik de abc-formule met i = √(-1):")
                
                x1 = (-b - sp.I * sp.sqrt(-D)) / (2*a)
                x2 = (-b + sp.I * sp.sqrt(-D)) / (2*a)
                x1_p, x2_p = pretty(sp.simplify(x1)), pretty(sp.simplify(x2))
                D_neg = pretty(-D)
                
                stappen.append("")
                stappen.append("📝 **Stap 4:** Bereken x₁ en x₂")
                stappen.append(f"   x₁ = [{b_neg} - i·√{D_neg}] / (2·{a_p}) = {x1_p}")
                stappen.append(f"   x₂ = [{b_neg} + i·√{D_neg}] / (2·{a_p}) = {x2_p}")
                stappen.append("")
                stappen.append(f"✅ **Oplossing:** x = {x1_p} of x = {x2_p}")
            
            return "\n".join(stappen)
        
        # Geen kwadratisch, gebruik algemene oplosser
        return los_op_met_stappen(vergelijking)
        
    except Exception as e:
        return f"Fout bij oplossen: {e}"

# --------------------------------------------
# TAYLOR/MACLAURIN
# --------------------------------------------
def doe_taylor_met_stappen(z):
    try:
        if "rond" not in z:
            return "Gebruik: taylor <functie> rond <punt> tot <n>"
        
        functie_deel, rest = z.split("rond", 1)
        functie = functie_deel.replace("taylor", "").strip()
        
        if "tot" not in rest:
            return "Gebruik: taylor <functie> rond <punt> tot <n>"
        
        punt_deel, n_deel = rest.split("tot", 1)
        punt = punt_deel.strip()
        n = int(n_deel.strip())
        
        x = sp.Symbol('x')
        f = expr(functie)
        a = expr(punt)
        
        stappen = []
        stappen.append("📐 **Taylorreeks ontwikkeling**")
        stappen.append("")
        stappen.append(f"De Taylorreeks van f(x) = {pretty(f)} rond x = {pretty(a)} tot de {n}e orde:")
        stappen.append("")
        stappen.append("📝 **Formule:**")
        stappen.append("   f(x) = Σ_{k=0}^{∞} f^({k})(a)/k! · (x-a)^k")
        stappen.append("   = f(a) + f'(a)(x-a) + f''(a)(x-a)²/2! + f'''(a)(x-a)³/3! + ...")
        stappen.append("")
        
        termen = []
        for k in range(n + 1):
            if k == 0:
                afgeleide = f.subs(x, a)
                term = afgeleide
                label = f"f({pretty(a)})"
            else:
                afgeleide = sp.diff(f, x, k).subs(x, a)
                if afgeleide != 0:
                    term = (afgeleide / sp.factorial(k)) * (x - a)**k
                    label = f"f^({k})({pretty(a)})/({k}!) · (x-{pretty(a)})^{k}"
                else:
                    term = 0
                    label = f"f^({k})({pretty(a)}) = 0 → term valt weg"
            
            if term != 0:
                termen.append((k, label, term))
        
        stappen.append("🔢 **Berekening van de termen:**")
        for k, label, term in termen:
            stappen.append(f"   Term {k}: {label} = {pretty(term)}")
        
        stappen.append("")
        
        if termen:
            taylor = sum(term for _, _, term in termen)
            taylor_simp = sp.simplify(taylor)
            
            stappen.append("📝 **Taylorreeks (uitgewerkt):**")
            stappen.append(f"   {pretty(taylor)}")
            stappen.append("")
            stappen.append("✅ **Vereenvoudigd:**")
            stappen.append(f"   {pretty(taylor_simp)}")
            
            if n > 0:
                stappen.append("")
                stappen.append(f"📌 **Notatie met foutterm:**")
                stappen.append(f"   f(x) = {pretty(taylor_simp)} + O((x-{pretty(a)})^{n+1})")
        else:
            stappen.append("⚠️ **Alle termen vallen weg (f(x) = 0)**")
        
        return "\n".join(stappen)
    except ValueError:
        return "Ongeldig getal voor 'tot'. Gebruik een heel getal."
    except Exception as e:
        return f"Fout bij Taylorreeks: {e}"

def doe_macklaurin_met_stappen(z):
    try:
        if "tot" in z:
            functie_deel, n_deel = z.split("tot", 1)
            functie = functie_deel.replace("macklaurin", "").strip()
            n = int(n_deel.strip())
            return doe_taylor_met_stappen(f"taylor {functie} rond 0 tot {n}")
        return "Gebruik: macklaurin <functie> tot <n>"
    except ValueError:
        return "Ongeldig getal voor 'tot'. Gebruik een heel getal."
    except Exception as e:
        return f"Fout bij Macklaurinreeks: {e}"

# --------------------------------------------
# PARSER
# --------------------------------------------
def SemCAS(z):
    global ANGLE_MODE
    zl = z.lower().strip()

    if zl.startswith("mode "):
        m = zl.split()[1]
        if m in ["rad", "deg"]:
            ANGLE_MODE = m
            return f"Hoekmodus ingesteld op {m}."
        return "Ongeldige modus. Gebruik 'mode rad' of 'mode deg'."

    if zl.startswith("pyth"):
        return doe_pyth(z)

    if zl.startswith("taylor"):
        return doe_taylor_met_stappen(z)
    if zl.startswith("macklaurin"):
        return doe_macklaurin_met_stappen(z)

    if zl.startswith("differentieer met stappen"):
        return doe_diff_met_stappen(z[26:].strip())
    if zl.startswith("differentieer"):
        return doe_diff(z[14:].strip())

    if zl.startswith("integreer met stappen"):
        return doe_int_met_stappen(z[22:].strip())
    if zl.startswith("integreer"):
        return doe_int(z[10:].strip())

    if zl.startswith("vereenvoudig met stappen"):
        return doe_simpel_met_stappen(z[25:].strip())
    if zl.startswith("vereenvoudig"):
        return doe_simpel(z[13:].strip())

    if zl.startswith("breid uit met stappen"):
        return doe_expand_met_stappen(z[22:].strip())
    if zl.startswith("breid uit"):
        delen = z.split(" ", 2)
        if len(delen) >= 3:
            return doe_expand(delen[2])
        return "Gebruik: breid uit <expressie>"
    if zl.startswith("expand "):
        return doe_expand(z.split(" ", 1)[1])

    if zl.startswith("factoriseer met stappen"):
        return doe_factor_met_stappen(z[24:].strip())
    if zl.startswith("factoriseer"):
        return doe_factor(z[12:].strip())

    # LIMIET
    if "wat is de limiet van" in zl:
        met_stappen = "met stappen" in zl
        z_clean = z.replace("met stappen", "").strip()
        parts = z_clean.split(" als ", 1)
        if len(parts) != 2:
            return "Gebruik: wat is de limiet van <expr> als <var> naar <waarde> gaat"
        e = parts[0].replace("wat is de limiet van", "").strip()
        rest = parts[1].strip()
        if " naar " not in rest:
            return "Gebruik: wat is de limiet van <expr> als <var> naar <waarde> gaat"
        var, rest2 = rest.split(" naar ", 1)
        var = var.strip()
        richting = rest2.replace("gaat", "").strip()
        if met_stappen:
            return doe_limiet_met_stappen(e, var, richting)
        return doe_limiet(e, var, richting)

    # OPLOSSEN
    if zl.startswith("los ") and zl.endswith(" op"):
        inhoud = z[4:-3].strip()
        return los_kwadratisch_op_met_stappen(inhoud)

    if zl.startswith("los ") and " op voor " in zl:
        inhoud = z[4:].strip()
        return los_kwadratisch_op_met_stappen(inhoud)

    # FALLBACK
    try:
        return doe_simpel(z)
    except sp.SympifyError:
        return "Syntaxfout."
    except ZeroDivisionError:
        return "Deling door nul."
    except KeyError:
        return "Onbekende variabele."
    except Exception as e:
        return f"Fout: {e}"

# --------------------------------------------
# REPL
# --------------------------------------------
print("=" * 60)
print("SemCAS 11.1 — NL geladen (ULTIMATE)")
print("=" * 60)
print("Typ 'stop' om te stoppen.")
print("")
print("📚 **Alle commando's met en zonder stappen:**")
print("")
print("  differentieer x^3 + 2x")
print("  differentieer met stappen x^3 + 2x")
print("")
print("  integreer x^2 + 3x")
print("  integreer met stappen x^2 + 3x")
print("")
print("  vereenvoudig (x+1)^2 - 1")
print("  vereenvoudig met stappen (x+1)^2 - 1")
print("")
print("  breid uit (x+2)^3")
print("  breid uit met stappen (x+2)^3")
print("")
print("  factoriseer x^2 - 4")
print("  factoriseer met stappen x^2 - 4")
print("")
print("  los 2x^2 - 4x - 6 = 0 op")
print("  los x^2 + 4x + 4 = 0 op")
print("  los 2x^2=7x^4 op")
print("")
print("  wat is de limiet van x^2 als x naar 2 gaat")
print("  wat is de limiet van sin(x)/x als x naar 0 gaat met stappen")
print("")
print("  taylor sin(x) rond 0 tot 4")
print("  macklaurin e^x tot 3")
print("")
print("  pyth a=3 b=4")
print("  mode rad / mode deg")
print("")
print("=" * 60)

while True:
    try:
        inp = input("SemCAS> ")
        if inp.lower() in ["stop", "exit", "quit"]:
            print("SemCAS afgesloten.")
            break
        if inp.strip() == "":
            continue
        print(SemCAS(inp))
    except KeyboardInterrupt:
        print("\nSemCAS afgesloten.")
        break
    except Exception as e:
        print(f"Onverwachte fout: {e}")