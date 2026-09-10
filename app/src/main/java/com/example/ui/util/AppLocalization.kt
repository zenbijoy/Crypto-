package com.example.ui.util

data class LanguageOption(
    val code: String,
    val displayName: String,
    val nativeName: String,
    val flag: String
)

object AppLocalization {
    val supportedLanguages = listOf(
        LanguageOption("en", "English", "English", "🇺🇸"),
        LanguageOption("es", "Español", "Español", "🇪🇸"),
        LanguageOption("fr", "Français", "Français", "🇫🇷"),
        LanguageOption("de", "Deutsch", "Deutsch", "🇩🇪"),
        LanguageOption("ja", "日本語", "日本語", "🇯🇵"),
        LanguageOption("ko", "한국어", "한국어", "🇰🇷"),
        LanguageOption("zh", "中文", "中文 (简体)", "🇨🇳"),
        LanguageOption("ru", "Русский", "Русский", "🇷🇺"),
        LanguageOption("vi", "Tiếng Việt", "Tiếng Việt", "🇻🇳"),
        LanguageOption("ar", "العربية", "العربية", "🇸🇦")
    )

    private val translations = mapOf(
        // Auth screen
        "welcome_back" to mapOf(
            "en" to "Welcome back",
            "es" to "Bienvenido de nuevo",
            "fr" to "Bon retour",
            "de" to "Willkommen zurück",
            "ja" to "お帰りなさい",
            "ko" to "다시 오신 것을 환영합니다",
            "zh" to "欢迎回来",
            "ru" to "С возвращением",
            "vi" to "Chào mừng trở lại",
            "ar" to "مرحباً بعودتك"
        ),
        "create_account_title" to mapOf(
            "en" to "Create your account",
            "es" to "Crea tu cuenta",
            "fr" to "Créez votre compte",
            "de" to "Erstellen Sie Ihr Konto",
            "ja" to "アカウントを作成する",
            "ko" to "계정을 만드세요",
            "zh" to "创建您的账户",
            "ru" to "Создайте свой аккаунт",
            "vi" to "Tạo tài khoản của bạn",
            "ar" to "أنشئ حسابك"
        ),
        "tagline" to mapOf(
            "en" to "Predict. Analyze. Trade Smarter.",
            "es" to "Predice. Analiza. Opera con Inteligencia.",
            "fr" to "Prédisez. Analysez. Tradez Intelligemment.",
            "de" to "Vorhersagen. Analysieren. Klüger Handeln.",
            "ja" to "予測・分析・スマートな取引。",
            "ko" to "예측. 분석. 더 스마트한 트레이딩.",
            "zh" to "预测 · 分析 · 智能交易",
            "ru" to "Прогнозируйте. Анализируйте. Торгуйте умнее.",
            "vi" to "Dự đoán. Phân tích. Giao dịch thông minh hơn.",
            "ar" to "تنبأ. حلل. تداول بذكاء."
        ),
        "signup_subtitle" to mapOf(
            "en" to "Join thousands of traders making\nsmarter decisions every day.",
            "es" to "Únete a miles de traders que toman\ndecisiones más inteligentes cada día.",
            "fr" to "Rejoignez des milliers de traders prenant\nde meilleures décisions chaque jour.",
            "de" to "Schließen Sie sich Tausenden von Händlern an,\ndie jeden Tag klügere Entscheidungen treffen.",
            "ja" to "毎日より賢明な判断を下す\n何千人ものトレーダーに参加しましょう。",
            "ko" to "매일 더 현명한 결정을 내리는\n수천 명의 트레이더와 함께하세요.",
            "zh" to "加入数千名交易员，\n每天做出更明智的决策。",
            "ru" to "Присоединяйтесь к тысячам трейдеров,\nпринимающих разумные решения каждый день.",
            "vi" to "Tham gia cùng hàng nghìn nhà giao dịch\nđưa ra quyết định thông minh hơn mỗi ngày.",
            "ar" to "انضم إلى آلاف المتداولين الذين يتخذون\nقرارات أكثر ذكاءً كل يوم."
        ),
        "signin_subtitle" to mapOf(
            "en" to "Log in to access your dashboard\nand AI-powered insights.",
            "es" to "Inicia sesión para acceder a tu panel\ny análisis impulsados por IA.",
            "fr" to "Connectez-vous pour accéder à votre tableau de bord\net analyses IA.",
            "de" to "Melden Sie sich an, um auf Ihr Dashboard\nund KI-Einblicke zuzugreifen.",
            "ja" to "ダッシュボードとAI分析にアクセスするには\nログインしてください。",
            "ko" to "대시보드와 AI 기반 통찰력에\n액세스하려면 로그인하세요.",
            "zh" to "登录以访问您的仪表盘\n和AI驱动的深度洞察。",
            "ru" to "Войдите, чтобы получить доступ к панели управления\nи аналитике ИИ.",
            "vi" to "Đăng nhập để truy cập trang tổng quan\nvà thông tin chi tiết bằng AI.",
            "ar" to "سجل الدخول للوصول إلى لوحة التحكم\nوالرؤى المدعومة بالذكاء الاصطناعي."
        ),
        "full_name" to mapOf(
            "en" to "Full Name",
            "es" to "Nombre completo",
            "fr" to "Nom complet",
            "de" to "Vollständiger Name",
            "ja" to "氏名",
            "ko" to "성명",
            "zh" to "全名",
            "ru" to "Полное имя",
            "vi" to "Họ và tên",
            "ar" to "الاسم الكامل"
        ),
        "email_address" to mapOf(
            "en" to "Email Address",
            "es" to "Correo electrónico",
            "fr" to "Adresse e-mail",
            "de" to "E-Mail-Adresse",
            "ja" to "メールアドレス",
            "ko" to "이메일 주소",
            "zh" to "电子邮箱",
            "ru" to "Электронная почта",
            "vi" to "Địa chỉ email",
            "ar" to "عنوان البريد الإلكتروني"
        ),
        "password" to mapOf(
            "en" to "Password",
            "es" to "Contraseña",
            "fr" to "Mot de passe",
            "de" to "Passwort",
            "ja" to "パスワード",
            "ko" to "비밀번호",
            "zh" to "密码",
            "ru" to "Пароль",
            "vi" to "Mật khẩu",
            "ar" to "كلمة المرور"
        ),
        "confirm_password" to mapOf(
            "en" to "Confirm Password",
            "es" to "Confirmar contraseña",
            "fr" to "Confirmer le mot de passe",
            "de" to "Passwort bestätigen",
            "ja" to "パスワード再入力",
            "ko" to "비밀번호 확인",
            "zh" to "确认密码",
            "ru" to "Подтвердите пароль",
            "vi" to "Xác nhận mật khẩu",
            "ar" to "تأكيد كلمة المرور"
        ),
        "forgot_password" to mapOf(
            "en" to "Forgot Password?",
            "es" to "¿Olvidaste tu contraseña?",
            "fr" to "Mot de passe oublié ?",
            "de" to "Passwort vergessen?",
            "ja" to "パスワードをお忘れですか？",
            "ko" to "비밀번호를 잊으셨나요?",
            "zh" to "忘记密码？",
            "ru" to "Забыли пароль?",
            "vi" to "Quên mật khẩu?",
            "ar" to "هل نسيت كلمة المرور؟"
        ),
        "log_in" to mapOf(
            "en" to "Log In",
            "es" to "Iniciar sesión",
            "fr" to "Connexion",
            "de" to "Anmelden",
            "ja" to "ログイン",
            "ko" to "로그인",
            "zh" to "登录",
            "ru" to "Войти",
            "vi" to "Đăng nhập",
            "ar" to "تسجيل الدخول"
        ),
        "create_account" to mapOf(
            "en" to "Create Account",
            "es" to "Crear cuenta",
            "fr" to "Créer un compte",
            "de" to "Konto erstellen",
            "ja" to "アカウント作成",
            "ko" to "계정 만들기",
            "zh" to "创建账户",
            "ru" to "Создать аккаунт",
            "vi" to "Tạo tài khoản",
            "ar" to "إنشاء حساب"
        ),
        "or_continue_with" to mapOf(
            "en" to "or continue with",
            "es" to "o continuar con",
            "fr" to "ou continuer avec",
            "de" to "oder weiter mit",
            "ja" to "または次で続行",
            "ko" to "또는 다음으로 계속",
            "zh" to "或继续使用",
            "ru" to "или продолжить через",
            "vi" to "hoặc tiếp tục với",
            "ar" to "أو تابع باستخدام"
        ),
        "dont_have_account" to mapOf(
            "en" to "Don't have an account? ",
            "es" to "¿No tienes una cuenta? ",
            "fr" to "Vous n'avez pas de compte ? ",
            "de" to "Kein Konto? ",
            "ja" to "アカウントをお持ちでないですか？ ",
            "ko" to "계정이 없으신가요? ",
            "zh" to "还没有账户？ ",
            "ru" to "Нет аккаунта? ",
            "vi" to "Chưa có tài khoản? ",
            "ar" to "ليس لديك حساب؟ "
        ),
        "already_have_account" to mapOf(
            "en" to "Already have an account? ",
            "es" to "¿Ya tienes una cuenta? ",
            "fr" to "Vous avez déjà un compte ? ",
            "de" to "Bereits ein Konto? ",
            "ja" to "既にアカウントをお持ちですか？ ",
            "ko" to "이미 계정이 있으신가요? ",
            "zh" to "已有账户？ ",
            "ru" to "Уже есть аккаунт? ",
            "vi" to "Đã có tài khoản? ",
            "ar" to "هل لديك حساب بالفعل؟ "
        ),
        "sign_up" to mapOf(
            "en" to "Sign up",
            "es" to "Regístrate",
            "fr" to "S'inscrire",
            "de" to "Registrieren",
            "ja" to "新規登録",
            "ko" to "가입하기",
            "zh" to "注册",
            "ru" to "Регистрация",
            "vi" to "Đăng ký",
            "ar" to "تسجيل"
        ),

        // Navigation tabs
        "nav_home" to mapOf(
            "en" to "Home",
            "es" to "Inicio",
            "fr" to "Accueil",
            "de" to "Startseite",
            "ja" to "ホーム",
            "ko" to "홈",
            "zh" to "首页",
            "ru" to "Главная",
            "vi" to "Trang chủ",
            "ar" to "الرئيسية"
        ),
        "nav_markets" to mapOf(
            "en" to "Markets",
            "es" to "Mercados",
            "fr" to "Marchés",
            "de" to "Märkte",
            "ja" to "市場",
            "ko" to "시세",
            "zh" to "行情",
            "ru" to "Рынки",
            "vi" to "Thị trường",
            "ar" to "الأسواق"
        ),
        "nav_orderflow" to mapOf(
            "en" to "OrderFlow",
            "es" to "Flujo de Órdenes",
            "fr" to "Flux d'Ordres",
            "de" to "OrderFlow",
            "ja" to "注文フロー",
            "ko" to "주문 흐름",
            "zh" to "订单流",
            "ru" to "Поток ордеров",
            "vi" to "Dòng lệnh",
            "ar" to "تدفق الأوامر"
        ),
        "nav_news" to mapOf(
            "en" to "News",
            "es" to "Noticias",
            "fr" to "Actualités",
            "de" to "Nachrichten",
            "ja" to "ニュース",
            "ko" to "뉴스",
            "zh" to "快讯",
            "ru" to "Новости",
            "vi" to "Tin tức",
            "ar" to "الأخبار"
        ),
        "nav_user_center" to mapOf(
            "en" to "User Center",
            "es" to "Perfil",
            "fr" to "Profil",
            "de" to "Profil",
            "ja" to "マイページ",
            "ko" to "사용자 센터",
            "zh" to "个人中心",
            "ru" to "Профиль",
            "vi" to "Cá nhân",
            "ar" to "الملف الشخصي"
        ),

        // Settings
        "settings_language" to mapOf(
            "en" to "Language",
            "es" to "Idioma",
            "fr" to "Langue",
            "de" to "Sprache",
            "ja" to "言語",
            "ko" to "언어",
            "zh" to "语言",
            "ru" to "Язык",
            "vi" to "Ngôn ngữ",
            "ar" to "اللغة"
        ),
        "settings_appearance" to mapOf(
            "en" to "Appearance",
            "es" to "Apariencia",
            "fr" to "Apparence",
            "de" to "Erscheinungsbild",
            "ja" to "外観",
            "ko" to "화면 설정",
            "zh" to "外观",
            "ru" to "Внешний вид",
            "vi" to "Giao diện",
            "ar" to "المظهر"
        ),
        "select_language_title" to mapOf(
            "en" to "Select Language",
            "es" to "Seleccionar idioma",
            "fr" to "Sélectionner la langue",
            "de" to "Sprache auswählen",
            "ja" to "言語を選択",
            "ko" to "언어 선택",
            "zh" to "选择语言",
            "ru" to "Выберите язык",
            "vi" to "Chọn ngôn ngữ",
            "ar" to "اختر اللغة"
        ),
        "cancel" to mapOf(
            "en" to "Cancel",
            "es" to "Cancelar",
            "fr" to "Annuler",
            "de" to "Abbrechen",
            "ja" to "キャンセル",
            "ko" to "취소",
            "zh" to "取消",
            "ru" to "Отмена",
            "vi" to "Hủy",
            "ar" to "إلغاء"
        )
    )

    fun getCode(languageName: String): String {
        return supportedLanguages.firstOrNull {
            it.displayName.equals(languageName, ignoreCase = true) ||
            it.nativeName.equals(languageName, ignoreCase = true) ||
            it.code.equals(languageName, ignoreCase = true)
        }?.code ?: "en"
    }

    fun tr(key: String, languageName: String): String {
        val code = getCode(languageName)
        val map = translations[key] ?: return key
        return map[code] ?: map["en"] ?: key
    }
}
