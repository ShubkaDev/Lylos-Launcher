APP_STYLE = r'''
* {
    font-family: "Segoe UI";
    color: #E5E7EB;
    font-size: 13px;
    outline: none;
}

QMainWindow {
    background-color: #020617;
}

QWidget {
    background-color: transparent;
}

QMainWindow::separator {
    background: rgba(148, 163, 184, 0.15);
    width: 1px;
    height: 1px;
}

#AppContent {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #020617,
        stop:0.42 #071427,
        stop:1 #130B20
    );
}

QScrollArea,
#ScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: rgba(15, 23, 42, 150);
    width: 10px;
    border-radius: 5px;
    margin: 4px 0 4px 0;
}

QScrollBar::handle:vertical {
    background: rgba(34, 211, 238, 165);
    border-radius: 5px;
    min-height: 28px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(34, 211, 238, 210);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical,
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    height: 0px;
    width: 0px;
    background: transparent;
}

QScrollBar:horizontal {
    background: rgba(15, 23, 42, 150);
    height: 10px;
    border-radius: 5px;
    margin: 0 4px;
}

QScrollBar::handle:horizontal {
    background: rgba(34, 211, 238, 165);
    border-radius: 5px;
    min-width: 28px;
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    background-color: rgba(10, 16, 32, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
    color: #F8FAFC;
    padding: 12px 14px;
    font-size: 14px;
    selection-background-color: rgba(139, 92, 246, 0.28);
}

QTextEdit,
QPlainTextEdit {
    padding: 10px 12px;
}

QLineEdit:hover,
QTextEdit:hover,
QPlainTextEdit:hover,
QComboBox:hover,
QSpinBox:hover,
QDoubleSpinBox:hover {
    border: 1px solid rgba(34, 211, 238, 0.35);
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 1px solid #8B5CF6;
    background-color: rgba(12, 20, 38, 0.92);
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #0B1427;
    border: 1px solid rgba(34, 211, 238, 0.24);
    border-radius: 12px;
    padding: 6px;
    selection-background-color: rgba(139, 92, 246, 0.22);
    selection-color: #F8FAFC;
}

QPushButton {
    border: none;
}

QPushButton:disabled {
    color: #64748B;
    border-color: rgba(100, 116, 139, 0.18);
    background-color: rgba(15, 23, 42, 0.45);
}

QCheckBox {
    spacing: 10px;
    color: #E2E8F0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 6px;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: rgba(15, 23, 42, 0.92);
}

QCheckBox::indicator:checked {
    background: #8B5CF6;
    border-color: #22D3EE;
}

QSlider::groove:horizontal {
    height: 8px;
    background: rgba(15, 23, 42, 0.85);
    border-radius: 4px;
}

QSlider::sub-page:horizontal {
    background: #8B5CF6;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #A5B4FC;
    border: 2px solid #8B5CF6;
    width: 22px;
    margin: -8px 0;
    border-radius: 11px;
}

QProgressBar {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 8px;
}

QProgressBar::chunk {
    background: #8B5CF6;
    border-radius: 8px;
}

QDialog, QMessageBox {
    background-color: #050C1B;
}

QTabWidget::pane,
QFrame#Card,
QFrame#Panel,
QFrame#DashboardPanel,
QFrame#MiniCard,
QFrame#SettingsOptionsBox,
QFrame#DownloadSummaryCard,
QFrame#InstanceCard,
QFrame#ModResultCard,
QFrame#DownloadTaskCard,
QFrame#DownloadTaskCardActive,
QFrame#HeroStatCard,
QFrame#SettingsStatCard,
QFrame#SkinCard,
QFrame#AccountRow,
QFrame#AccountRowActive,
QFrame#DetailInfoRow,
QWidget#InstanceCard,
QWidget#Card {
    background-color: rgba(10, 17, 32, 0.84);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 22px;
}

QFrame#DownloadTaskCardActive,
QFrame#AccountRowActive,
QFrame#InstanceDashboardRowActive,
QFrame#HeroStatCard:hover,
QFrame#DashboardPanel:hover,
QFrame#InstanceCard:hover,
QWidget#InstanceCard:hover,
QFrame#ModResultCard:hover,
QFrame#SkinCard:hover,
QFrame#DownloadSummaryCard:hover,
QFrame#DownloadTaskCard:hover,
QFrame#MiniCard:hover,
QFrame#Card:hover,
QWidget#Card:hover,
QFrame#SettingsStatCard:hover,
QFrame#DetailInfoRow:hover {
    border: 1px solid rgba(34, 211, 238, 0.32);
    background-color: rgba(11, 20, 37, 0.94);
}

#PageTitle {
    color: #F8FAFC;
    font-size: 40px;
    font-weight: 900;
    letter-spacing: 0.3px;
}

#PageDescription,
#PanelText,
#MutedText {
    color: #CBD5E1;
    font-size: 14px;
    line-height: 1.4em;
}

#PanelText,
#MutedText {
    color: #B6C2D1;
}

#SectionTitle,
#PanelTitle {
    color: #F8FAFC;
    font-size: 20px;
    font-weight: 900;
}

#CardTitle,
#InstanceTitle,
#SettingsSectionLabel {
    color: #F8FAFC;
    font-size: 16px;
    font-weight: 800;
}

#InstanceMeta,
#EmptyText {
    color: #8CA0B8;
    font-size: 12px;
    font-weight: 600;
}

#EmptyText {
    font-size: 14px;
}

#StatusBadge,
#SmallBadge,
#InstanceBadge,
#ModTag {
    background-color: rgba(124, 58, 237, 0.22);
    border: 1px solid rgba(34, 211, 238, 0.24);
    color: #E0F2FE;
    border-radius: 999px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 800;
}

#StatusBadge {
    padding: 7px 14px;
}

#DownloadBigNumber,
#HeroStatValue,
#SettingsRamValue {
    color: #F8FAFC;
    font-size: 18px;
    font-weight: 900;
}

#DownloadBigNumber {
    font-size: 28px;
}

#HeroStatTitle {
    color: #A9BDD4;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

#MiniProgress,
#BigProgress,
#DownloadProgress {
    background: rgba(15, 23, 42, 0.88);
    border: 1px solid rgba(148, 163, 184, 0.08);
    border-radius: 999px;
}

#MiniProgress::chunk,
#BigProgress::chunk,
#DownloadProgress::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B5CF6,
        stop:1 #22D3EE
    );
    border-radius: 999px;
}

/* Sidebar */
#Sidebar {
    background-color: rgba(2, 6, 23, 0.98);
    border-right: 1px solid rgba(148, 163, 184, 0.12);
}

#SidebarLogoCard {
    background-color: rgba(11, 18, 32, 0.95);
    border: 1px solid rgba(139, 92, 246, 0.22);
    border-radius: 26px;
}

#SMLogoTitle {
    color: #F8FAFC;
    font-size: 25px;
    font-weight: 900;
    letter-spacing: 3px;
}

#SMLogoSubtitle {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}

#SidebarSectionTitle {
    color: #64748B;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 3px;
    padding-left: 8px;
}

#SidebarNavButton {
    text-align: left;
    color: #D5DFEB;
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 16px;
    padding: 0 16px;
    font-size: 14px;
    font-weight: 800;
}

#SidebarNavButton:hover {
    background-color: rgba(139, 92, 246, 0.08);
    border: 1px solid rgba(34, 211, 238, 0.2);
    color: #F8FAFC;
}

#SidebarNavButton[active="true"] {
    background-color: #8B5CF6;
    border: 1px solid #22D3EE;
    color: white;
}

#SidebarNavButton[disabledPage="true"] {
    color: #64748B;
}

#SidebarProfileCard {
    background-color: rgba(11, 18, 32, 0.96);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 20px;
}

#SidebarProfileName {
    color: #F8FAFC;
    font-size: 14px;
    font-weight: 900;
}

#SidebarProfileStatus {
    color: #A5B4FC;
    font-size: 12px;
    font-weight: 700;
}

#SidebarProfileArrow {
    color: #94A3B8;
    font-size: 16px;
    font-weight: 900;
}

/* Topbar */
#Topbar {
    background-color: rgba(2, 6, 23, 0.72);
    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

#TopbarTitle {
    color: #F8FAFC;
    font-size: 20px;
    font-weight: 900;
}

#TopbarSubtitle {
    color: #6B829B;
    font-size: 12px;
    font-weight: 700;
}

#TopbarSearch,
#SearchInput,
QLineEdit#Input {
    background-color: rgba(10, 17, 32, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
    color: #F8FAFC;
    padding: 12px 16px;
    font-size: 14px;
}

#TopbarSearch:focus,
#SearchInput:focus,
QLineEdit#Input:focus {
    border: 1px solid #8B5CF6;
}

#TopbarStatusButton {
    background-color: rgba(20, 83, 45, 0.32);
    border: 1px solid rgba(34, 211, 238, 0.24);
    border-radius: 16px;
    color: #E0F2FE;
    padding: 12px 18px;
    font-size: 13px;
    font-weight: 900;
}

#TopbarPlayButton,
#HeroPlayButton,
#PrimaryButton {
    background-color: #8B5CF6;
    border: 1px solid #22D3EE;
    border-radius: 16px;
    color: white;
    padding: 12px 22px;
    font-size: 14px;
    font-weight: 900;
}

#TopbarPlayButton {
    padding: 13px 28px;
    font-size: 15px;
}

#TopbarPlayButton:hover,
#HeroPlayButton:hover,
#PrimaryButton:hover {
    background-color: #7C3AED;
}

#SecondaryButton,
#SmallGhostButton,
#WideGhostButton,
#GhostButton {
    background-color: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
    color: #E2E8F0;
    padding: 11px 18px;
    font-size: 13px;
    font-weight: 800;
}

#SmallGhostButton {
    padding: 9px 14px;
    font-size: 12px;
}

#WideGhostButton {
    padding: 12px 18px;
}

#SecondaryButton:hover,
#SmallGhostButton:hover,
#WideGhostButton:hover,
#GhostButton:hover {
    border: 1px solid rgba(34, 211, 238, 0.3);
    background-color: rgba(17, 30, 54, 0.92);
}

#DangerButton {
    background-color: rgba(127, 29, 29, 0.38);
    border: 1px solid rgba(248, 113, 113, 0.28);
    border-radius: 16px;
    color: #FECACA;
    padding: 11px 18px;
    font-size: 13px;
    font-weight: 800;
}

#DangerButton:hover {
    background-color: rgba(153, 27, 27, 0.55);
}

/* Dashboard / Home */
#MinecraftHero {
    background-color: rgba(6, 14, 29, 0.98);
    border: 1px solid rgba(34, 211, 238, 0.16);
    border-radius: 30px;
}

#HeroWelcome {
    color: #B6C2D1;
    font-size: 16px;
    font-weight: 700;
}

#HeroTitle {
    color: #F8FAFC;
    font-size: 42px;
    font-weight: 900;
}

#HeroSubtitle {
    color: #D4DEE8;
    font-size: 15px;
}

#QuickActionCard,
#OverviewStatCard,
#ActivityRow,
#RecommendationRow,
#InstanceDashboardRow,
#InstanceDashboardRowActive {
    background-color: rgba(10, 17, 32, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 20px;
}

#QuickActionCard:hover,
#OverviewStatCard:hover,
#ActivityRow:hover,
#RecommendationRow:hover,
#InstanceDashboardRow:hover,
#InstanceDashboardRowActive:hover {
    border: 1px solid rgba(34, 211, 238, 0.26);
    background-color: rgba(11, 20, 37, 0.92);
}

#OverviewStatLabel {
    color: #8CA0B8;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

#OverviewStatValue {
    color: #F8FAFC;
    font-size: 26px;
    font-weight: 900;
}

#OverviewStatMeta,
#ActivityMeta {
    color: #A9BDD4;
    font-size: 12px;
}

#QuickActionTitle {
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 900;
}

#QuickActionText {
    color: #B8C4D5;
    font-size: 13px;
}

#BlockIcon,
#DownloadIcon,
#OverviewIcon,
#QuickActionIcon {
    background-color: rgba(20, 83, 45, 0.2);
    border: 1px solid rgba(34, 211, 238, 0.18);
    border-radius: 14px;
    color: #E0F2FE;
}

#MiniPlayButton {
    background-color: rgba(139, 92, 246, 0.16);
    border: 1px solid rgba(34, 211, 238, 0.24);
    border-radius: 12px;
}

#MiniPlayButton:hover {
    background-color: rgba(139, 92, 246, 0.28);
}

/* Mods */
#ModIconImage,
#ModIconBox,
#ModDetailsIcon,
#ModScreenshot {
    background-color: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 16px;
}

#ModDescriptionBox,
#LogViewer {
    background-color: rgba(5, 10, 22, 0.96);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 18px;
    color: #DDE6F1;
}

#LogViewer {
    font-family: "Consolas", "JetBrains Mono", monospace;
    font-size: 12px;
    line-height: 1.3em;
}

#DownloadStatus {
    color: #DDE6F1;
    font-size: 13px;
    font-weight: 700;
}

#DownloadError {
    background: rgba(127, 29, 29, 0.22);
    border: 1px solid rgba(248, 113, 113, 0.18);
    border-radius: 14px;
    color: #FECACA;
    padding: 10px 12px;
}

#BottomStatusBar {
    background-color: rgba(2, 6, 23, 0.88);
    border-top: 1px solid rgba(148, 163, 184, 0.12);
}

#BottomStatusText {
    color: #94A3B8;
    font-size: 12px;
    font-weight: 700;
}

/* Detail pages and tabs */
#InstanceDetailHero {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(10, 17, 32, 0.96),
        stop:0.55 rgba(11, 26, 45, 0.94),
        stop:1 rgba(20, 83, 45, 0.28)
    );
    border: 1px solid rgba(34, 211, 238, 0.2);
    border-radius: 28px;
}

#InstanceDetailTabs::pane {
    background-color: rgba(10, 17, 32, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 22px;
    top: -1px;
}

QTabBar::tab {
    background-color: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.14);
    color: #A9BDD4;
    border-top-left-radius: 14px;
    border-top-right-radius: 14px;
    padding: 10px 15px;
    margin-right: 4px;
    font-weight: 800;
}

QTabBar::tab:hover {
    color: #F8FAFC;
    border-color: rgba(34, 211, 238, 0.25);
}

QTabBar::tab:selected {
    background-color: rgba(139, 92, 246, 0.2);
    color: #E0F2FE;
    border-color: rgba(34, 211, 238, 0.34);
}

#AccountRow, #AccountRowActive, #SkinCard {
    background-color: rgba(10, 17, 32, 0.84);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 20px;
}

#AccountRowActive {
    border: 1px solid rgba(34, 211, 238, 0.32);
    background-color: rgba(20, 83, 45, 0.18);
}

#Card {
    background-color: rgba(10, 17, 32, 0.84);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 22px;
}

#Input {
    background-color: rgba(10, 16, 32, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
    color: #F8FAFC;
    padding: 10px 14px;
}

#MiniCard {
    background-color: rgba(10, 17, 32, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 20px;
}

/* Mods page compact UI */
#ToggleFiltersButton {
    background-color: rgba(139, 92, 246, 0.15);
    border: 1px solid rgba(34, 211, 238, 0.30);
    border-radius: 16px;
    color: #E0F2FE;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 800;
}
#ToggleFiltersButton:hover {
    background-color: rgba(139, 92, 246, 0.28);
    border: 1px solid rgba(34, 211, 238, 0.50);
}

#CompactStatus {
    color: #8CA0B8;
    font-size: 12px;
    font-weight: 700;
    padding: 0 8px;
}

#ModsAdvancedFilters {
    background: transparent;
    border: none;
}

/* Update bar */
#UpdateBar {
    background-color: rgba(139, 92, 246, 0.10);
    border-bottom: 1px solid rgba(34, 211, 238, 0.20);
}
#UpdateBarReady {
    background-color: rgba(139, 92, 246, 0.18);
    border-bottom: 1px solid rgba(34, 211, 238, 0.35);
}
#UpdateStatusText {
    color: #E0F2FE;
    font-size: 12px;
    font-weight: 700;
}
#BottomStatusText {
    color: #8CA0B8;
    font-size: 11px;
    font-weight: 600;
}

'''


def _read_saved_theme():
    try:
        import json
        from storage.paths import DATA_DIR
        settings_file = DATA_DIR / "launcher_settings.json"
        if not settings_file.exists():
            return "dark"
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        theme = str(data.get("theme", "dark")).lower()
        if theme == "light":
            return "dark"
        return theme
    except Exception:
        return "dark"


def _theme_overlay(name, bg0, bg1, bg2, sidebar, panel, panel_hover, accent, accent2, border, text, muted):
    return f"""
/* LL theme: {name} */
QMainWindow {{
    background-color: {bg0};
}}
#AppContent {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {bg0}, stop:0.45 {bg1}, stop:1 {bg2});
}}
#Sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {sidebar}, stop:0.58 {bg0}, stop:1 #05060E);
    border-right: 1px solid {border};
}}
#Topbar, #BottomStatusBar {{
    background-color: rgba(6, 10, 12, 0.94);
    border-color: {border};
}}
QFrame#Card, QFrame#Panel, QFrame#DashboardPanel, QFrame#MiniCard,
QFrame#SettingsOptionsBox, QFrame#DownloadSummaryCard, QFrame#InstanceCard,
QFrame#ModResultCard, QFrame#DownloadTaskCard, QFrame#DownloadTaskCardActive,
QFrame#HeroStatCard, QFrame#SettingsStatCard, QFrame#SkinCard,
QFrame#AccountRow, QFrame#AccountRowActive, QFrame#DetailInfoRow,
QFrame#QuickActionCard, QFrame#OverviewStatCard, QFrame#ActivityRow,
QFrame#RecommendationRow, QFrame#InstanceDashboardRow,
QFrame#InstanceDashboardRowActive, QWidget#InstanceCard, QWidget#Card {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {panel_hover}, stop:1 {panel});
    border: 1px solid {border};
    border-radius: 17px;
}}
QFrame#Card:hover, QFrame#Panel:hover, QFrame#DashboardPanel:hover,
QFrame#MiniCard:hover, QFrame#InstanceCard:hover, QFrame#ModResultCard:hover,
QFrame#QuickActionCard:hover, QFrame#OverviewStatCard:hover,
QFrame#InstanceDashboardRow:hover, QFrame#InstanceDashboardRowActive:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {panel_hover}, stop:1 {bg1});
    border: 1px solid {accent2};
}}
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
#TopbarSearch, #SearchInput, QLineEdit#Input {{
    background-color: rgba(3, 7, 10, 0.86);
    border: 1px solid {border};
    color: {text};
    selection-background-color: {accent};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDoubleSpinBox:focus, #TopbarSearch:focus, #SearchInput:focus {{
    border: 1px solid {accent2};
    background-color: rgba(8, 14, 18, 0.98);
}}
#PrimaryButton, #HeroPlayButton, #TopbarPlayButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {accent}, stop:1 {accent2});
    border: 1px solid {accent2};
    color: #12081F;
}}
#PrimaryButton:hover, #HeroPlayButton:hover, #TopbarPlayButton:hover {{
    background: {accent2};
}}
#SecondaryButton, #GhostButton, #SmallGhostButton, #WideGhostButton,
#TopbarThemeButton, #TopbarMenuButton, #TopbarStatusButton, #ToggleFiltersButton {{
    background-color: rgba(5, 10, 13, 0.92);
    border: 1px solid {border};
    color: {text};
}}
#SecondaryButton:hover, #GhostButton:hover, #SmallGhostButton:hover,
#WideGhostButton:hover, #TopbarThemeButton:hover, #TopbarMenuButton:hover,
#TopbarStatusButton:hover, #ToggleFiltersButton:hover {{
    background-color: {panel_hover};
    border-color: {accent2};
}}
#SidebarLogoCard, #SidebarProfileCard {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {panel_hover}, stop:1 {panel});
    border: 1px solid {border};
}}
#SidebarNavButton[active="true"], #SidebarProfileCard[active="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {accent}, stop:1 {accent2});
    border-color: {accent2};
    color: #12081F;
}}
#PageTitle, #HeroTitle, #PanelTitle, #SectionTitle, #CardTitle,
#InstanceTitle, #TopbarTitle, #SidebarProfileName {{
    color: {text};
}}
#PageDescription, #PanelText, #MutedText, #InstanceMeta,
#TopbarSubtitle, #SidebarProfileStatus {{
    color: {muted};
}}
#StatusBadge, #SmallBadge, #InstanceBadge, #ModTag {{
    background-color: {panel_hover};
    border: 1px solid {border};
    color: {text};
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal,
QProgressBar::chunk, #MiniProgress::chunk, #BigProgress::chunk, #DownloadProgress::chunk {{
    background: {accent};
}}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
    background: {accent2};
}}
"""


DARK_STYLE = _theme_overlay(
    "dark",
    "#0B0E1A", "#141A2E", "#1E2440", "#070A12",
    "rgba(12, 16, 30, 0.94)", "rgba(24, 30, 56, 0.96)",
    "#8B5CF6", "#22D3EE", "rgba(148, 163, 184, 0.24)",
    "#F5F3FF", "#94A3B8",
)

AMOLED_STYLE = _theme_overlay(
    "amoled",
    "#000000", "#020617", "#07030D", "#000000",
    "rgba(2, 6, 12, 0.96)", "rgba(8, 13, 23, 0.98)",
    "#8B5CF6", "#A5B4FC", "rgba(34, 211, 238, 0.24)",
    "#F5FFF8", "#A7B8AC",
)

THEME_OPTIONS = [
    ("dark", "LL Тёмная"),
    ("amoled", "LL AMOLED"),
    ("forest", "LL Deep Violet"),
    ("ocean", "LL Океан"),
    ("purple", "LL Эндер"),
    ("sunset", "LL Закат"),
]

FOREST_STYLE = _theme_overlay("forest", "#0F0A1E", "#1A1033", "#271745", "#07030D", "rgba(18, 12, 36, 0.94)", "rgba(38, 26, 70, 0.96)", "#8B5CF6", "#A5B4FC", "rgba(139, 92, 246, 0.25)", "#F5F3FF", "#B8A8E8")
OCEAN_STYLE = _theme_overlay("ocean", "#061018", "#0A2030", "#082B36", "#030912", "rgba(7, 20, 31, 0.94)", "rgba(12, 48, 62, 0.96)", "#2F86A6", "#7DD3FC", "rgba(125, 211, 252, 0.22)", "#ECFEFF", "#A7C8D9")
PURPLE_STYLE = _theme_overlay("purple", "#100817", "#1C0D2B", "#2A1236", "#09050E", "rgba(22, 12, 34, 0.94)", "rgba(55, 28, 78, 0.96)", "#8257C2", "#C084FC", "rgba(192, 132, 252, 0.24)", "#FAF5FF", "#CAB7DF")
SUNSET_STYLE = _theme_overlay("sunset", "#170B07", "#2A1610", "#3A2412", "#0D0705", "rgba(34, 16, 10, 0.94)", "rgba(75, 43, 20, 0.96)", "#B87333", "#F6AD55", "rgba(246, 173, 85, 0.24)", "#FFF7ED", "#DFC3A7")


COMFORT_STYLE = '\n/* LL Comfort Minecraft UI Patch */\n* {\n    font-size: 12px;\n}\n\n#AppContent {\n    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0F0A1E, stop:0.45 #071827, stop:1 #120A1B);\n}\n\nQScrollBar:horizontal {\n    height: 0px;\n    background: transparent;\n}\nQScrollBar::handle:horizontal {\n    height: 0px;\n    background: transparent;\n}\n\nQFrame#DashboardPanel,\nQFrame#Panel,\nQFrame#Card,\nQFrame#MiniCard,\nQFrame#DownloadSummaryCard,\nQFrame#InstanceCard,\nQFrame#ModResultCard,\nQFrame#DownloadTaskCard,\nQFrame#HeroStatCard,\nQFrame#SettingsStatCard,\nQFrame#QuickActionCard,\nQFrame#OverviewStatCard,\nQFrame#ActivityRow,\nQFrame#RecommendationRow,\nQFrame#InstanceDashboardRow,\nQFrame#InstanceDashboardRowActive,\nQWidget#Card {\n    border-radius: 16px;\n    background-color: rgba(8, 17, 31, 0.82);\n    border: 1px solid rgba(129, 140, 248, 0.22);\n}\n\nQFrame#DashboardPanel:hover,\nQFrame#ModResultCard:hover,\nQFrame#QuickActionCard:hover,\nQFrame#OverviewStatCard:hover,\nQFrame#InstanceDashboardRow:hover,\nQFrame#InstanceDashboardRowActive:hover {\n    border: 1px solid rgba(103, 232, 249, 0.42);\n    background-color: rgba(10, 23, 38, 0.92);\n}\n\n#Sidebar {\n    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0A0D1A, stop:0.55 #04050C, stop:1 #000000);\n}\n\n#SidebarLogoCard {\n    border-radius: 20px;\n    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(13, 31, 23, 0.96), stop:1 rgba(8, 15, 29, 0.96));\n}\n\n#SidebarProfileCard {\n    border-radius: 18px;\n    background-color: rgba(10, 18, 32, 0.94);\n}\n#SidebarProfileCard[active="true"] {\n    border: 1px solid rgba(34, 211, 238, 0.62);\n    background-color: rgba(124, 58, 237, 0.28);\n}\n\n#SidebarNavButton {\n    border-radius: 14px;\n    padding: 0 13px;\n    font-size: 13px;\n}\n#SidebarNavButton[active="true"] {\n    color: #140A24;\n    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #A5B4FC);\n}\n\n#Topbar {\n    background-color: rgba(5, 12, 24, 0.88);\n}\n#TopbarTitle {\n    font-size: 18px;\n}\n#TopbarSubtitle {\n    font-size: 11px;\n}\n\n#PageTitle {\n    font-size: 30px;\n    letter-spacing: 0px;\n}\n#HeroTitle {\n    font-size: 34px;\n}\n#PanelTitle,\n#SectionTitle {\n    font-size: 18px;\n}\n#CardTitle,\n#InstanceTitle,\n#QuickActionTitle {\n    font-size: 15px;\n}\n#PageDescription,\n#PanelText,\n#MutedText,\n#QuickActionText {\n    font-size: 12px;\n}\n#OverviewStatValue,\n#DownloadBigNumber {\n    font-size: 22px;\n}\n#HeroStatValue,\n#SettingsRamValue {\n    font-size: 16px;\n}\n#HeroStatTitle,\n#OverviewStatLabel {\n    font-size: 10px;\n    letter-spacing: 0.8px;\n}\n\nQLineEdit,\nQTextEdit,\nQPlainTextEdit,\nQComboBox,\n#TopbarSearch,\n#SearchInput,\nQLineEdit#Input {\n    border-radius: 13px;\n    padding: 9px 12px;\n    font-size: 12px;\n    min-height: 22px;\n}\n\n#TopbarThemeButton,\n#TopbarStatusButton,\n#TopbarPlayButton,\n#HeroPlayButton,\n#PrimaryButton,\n#SecondaryButton,\n#SmallGhostButton,\n#WideGhostButton,\n#GhostButton,\n#DangerButton {\n    border-radius: 13px;\n    padding: 9px 14px;\n    font-size: 12px;\n}\n\n#TopbarThemeButton {\n    background-color: rgba(15, 23, 42, 0.78);\n    border: 1px solid rgba(148, 163, 184, 0.18);\n    color: #E0F2FE;\n    font-weight: 900;\n}\n\n#TopbarPlayButton {\n    padding: 10px 22px;\n    color: #140A24;\n}\n\n#MinecraftHero {\n    border-radius: 20px;\n    background-color: rgba(7, 19, 22, 0.90);\n}\n\n#HeroWelcome {\n    font-size: 13px;\n}\n\n#HeroSubtitle {\n    font-size: 13px;\n}\n\n#StatusBadge,\n#SmallBadge,\n#InstanceBadge,\n#ModTag {\n    padding: 4px 9px;\n    border-radius: 8px;\n    font-size: 11px;\n    background-color: rgba(139, 92, 246, 0.12);\n}\n\n#OverviewIcon,\n#QuickActionIcon,\n#BlockIcon,\n#DownloadIcon,\n#HeroStatIcon {\n    border-radius: 10px;\n}\n\n#MinecraftShortcutCard {\n    text-align: left;\n    background-color: rgba(14, 24, 39, 0.88);\n    border: 1px solid rgba(129, 140, 248, 0.22);\n    border-radius: 16px;\n    color: #E8F0FF;\n    padding: 12px 14px;\n    font-size: 12px;\n    font-weight: 800;\n}\n#MinecraftShortcutCard:hover {\n    background-color: rgba(124, 58, 237, 0.23);\n    border-color: rgba(34, 211, 238, 0.42);\n}\n\n#ToggleFiltersButton {\n    background-color: rgba(139, 92, 246, 0.15);\n    border: 1px solid rgba(34, 211, 238, 0.30);\n    border-radius: 13px;\n    color: #E0F2FE;\n    padding: 8px 14px;\n    font-size: 12px;\n    font-weight: 800;\n}\n#ToggleFiltersButton:hover {\n    background-color: rgba(139, 92, 246, 0.28);\n    border: 1px solid rgba(34, 211, 238, 0.50);\n}\n\n#CompactStatus {\n    color: #8CA0B8;\n    font-size: 11px;\n    font-weight: 700;\n    padding: 0 6px;\n}\n\n#ModsAdvancedFilters {\n    background: transparent;\n    border: none;\n}\n\n#ModResultCard {\n    border-radius: 18px;\n}\n#ModIconImage,\n#ModIconBox,\n#ModDetailsIcon {\n    border-radius: 12px;\n}\n\nQProgressBar,\n#MiniProgress,\n#BigProgress,\n#DownloadProgress {\n    max-height: 7px;\n    border-radius: 4px;\n}\n\n#BottomStatusBar {\n    min-height: 24px;\n    max-height: 28px;\n}\n'


MINECRAFT_CLEAN_STYLE = r"""
/* LL Minecraft Clean Fix: stable, readable, non-neon UI */

* {
    font-family: "Segoe UI";
    font-size: 12px;
    color: #E5E7EB;
}

/* Main surfaces */
QMainWindow {
    background-color: #0B0E1A;
}

#AppContent {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0E1224,
        stop:0.48 #161C36,
        stop:1 #1C1440
    );
}

QWidget {
    background-color: transparent;
}

/* Scrollbars: calm grass accent, not neon */
QScrollBar:vertical {
    background: rgba(11, 14, 26, 130);
    width: 9px;
    border-radius: 4px;
    margin: 4px 2px 4px 2px;
}
QScrollBar::handle:vertical {
    background: rgba(139, 92, 246, 175);
    border-radius: 4px;
    min-height: 32px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(167, 139, 250, 215);
}
QScrollBar:horizontal {
    background: rgba(11, 14, 26, 120);
    height: 8px;
    border-radius: 4px;
    margin: 2px 4px;
}
QScrollBar::handle:horizontal {
    background: rgba(139, 92, 246, 175);
    border-radius: 4px;
    min-width: 32px;
}

/* Cards and panels */
QFrame#Card,
QFrame#Panel,
QFrame#DashboardPanel,
QFrame#MiniCard,
QFrame#SettingsOptionsBox,
QFrame#DownloadSummaryCard,
QFrame#InstanceCard,
QFrame#ModResultCard,
QFrame#DownloadTaskCard,
QFrame#DownloadTaskCardActive,
QFrame#HeroStatCard,
QFrame#SettingsStatCard,
QFrame#SkinCard,
QFrame#AccountRow,
QFrame#AccountRowActive,
QFrame#DetailInfoRow,
QFrame#QuickActionCard,
QFrame#OverviewStatCard,
QFrame#ActivityRow,
QFrame#RecommendationRow,
QFrame#InstanceDashboardRow,
QFrame#InstanceDashboardRowActive,
QWidget#InstanceCard,
QWidget#Card {
    background-color: rgba(15, 18, 34, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 14px;
}

QFrame#Card:hover,
QFrame#Panel:hover,
QFrame#DashboardPanel:hover,
QFrame#MiniCard:hover,
QFrame#InstanceCard:hover,
QFrame#ModResultCard:hover,
QFrame#QuickActionCard:hover,
QFrame#OverviewStatCard:hover,
QFrame#InstanceDashboardRow:hover,
QFrame#InstanceDashboardRowActive:hover,
QWidget#InstanceCard:hover,
QWidget#Card:hover {
    background-color: rgba(20, 22, 44, 0.96);
    border: 1px solid rgba(129, 140, 248, 0.36);
}

/* Sidebar */
#Sidebar {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #0A0D18,
        stop:0.56 #070811,
        stop:1 #05060E
    );
    border-right: 1px solid rgba(148, 163, 184, 0.15);
}

#SidebarLogoCard {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(27, 20, 52, 0.98),
        stop:1 rgba(20, 18, 40, 0.98)
    );
    border: 1px solid rgba(129, 140, 248, 0.28);
    border-radius: 18px;
}

#SMMark,
#SidebarAvatar {
    background-color: rgba(124, 58, 237, 0.24);
    border: 1px solid rgba(103, 232, 249, 0.38);
    border-radius: 13px;
}

#SMLogoTitle {
    color: #F5F3FF;
    letter-spacing: 4px;
    font-weight: 950;
}

#SMLogoSubtitle,
#SidebarSectionTitle {
    color: #94A3B8;
    letter-spacing: 3px;
}

#SidebarNavButton {
    background-color: transparent;
    color: #D7DDE9;
    border: 1px solid transparent;
    border-radius: 12px;
    padding: 0 12px;
    text-align: left;
    font-size: 12px;
    font-weight: 750;
    min-height: 42px;
}

#SidebarNavButton:hover {
    background-color: rgba(124, 58, 237, 0.14);
    border: 1px solid rgba(148, 163, 184, 0.18);
}

#SidebarNavButton[active="true"] {
    color: #FFFFFF;
    background: #7C3AED;
    border: 1px solid rgba(196, 181, 253, 0.28);
}

#SidebarProfileCard {
    background-color: rgba(15, 18, 34, 0.94);
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 14px;
}

#SidebarProfileCard[active="true"] {
    background-color: rgba(76, 29, 149, 0.38);
    border-color: rgba(34, 211, 238, 0.44);
}

/* Topbar: compact and readable */
#Topbar {
    background-color: rgba(10, 13, 26, 0.92);
    border-bottom: 1px solid rgba(148, 163, 184, 0.14);
}

#TopbarTitle {
    color: #F5F3FF;
    font-size: 18px;
    font-weight: 900;
}

#TopbarSubtitle {
    color: #A6B2C6;
    font-size: 11px;
}

#TopbarSearch,
QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QLineEdit#Input,
#SearchInput {
    background-color: rgba(8, 10, 20, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 12px;
    color: #EFF4FC;
    padding: 8px 12px;
    font-size: 12px;
    min-height: 22px;
    selection-background-color: rgba(139, 92, 246, 0.45);
}

#TopbarSearch:focus,
QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus {
    border: 1px solid rgba(34, 211, 238, 0.58);
    background-color: rgba(10, 13, 26, 0.95);
}

/* Buttons */
#PrimaryButton,
#HeroPlayButton,
#TopbarPlayButton {
    background: #8B5CF6;
    color: #FFFFFF;
    border: 1px solid rgba(196, 181, 253, 0.25);
    border-radius: 12px;
    padding: 8px 15px;
    font-size: 12px;
    font-weight: 850;
}

#PrimaryButton:hover,
#HeroPlayButton:hover,
#TopbarPlayButton:hover {
    background: #06B6D4;
    border-color: rgba(207, 225, 178, 0.34);
}

#SecondaryButton,
#GhostButton,
#SmallGhostButton,
#WideGhostButton,
#TopbarThemeButton,
#TopbarMenuButton,
#TopbarStatusButton,
#DangerButton,
#ToggleFiltersButton {
    background-color: rgba(12, 15, 30, 0.86);
    color: #E8EDF8;
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 12px;
    padding: 8px 13px;
    font-size: 12px;
    font-weight: 800;
}

#SecondaryButton:hover,
#GhostButton:hover,
#SmallGhostButton:hover,
#WideGhostButton:hover,
#TopbarThemeButton:hover,
#TopbarMenuButton:hover,
#TopbarStatusButton:hover,
#ToggleFiltersButton:hover {
    background-color: rgba(124, 58, 237, 0.18);
    border-color: rgba(34, 211, 238, 0.38);
}

#CollapsibleHeader {
    background-color: rgba(14, 17, 33, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 18px;
}

#TopbarMenuButton {
    min-width: 38px;
    max-width: 46px;
    font-size: 17px;
    font-weight: 950;
}

#SidebarCollapseButton {
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
    border-radius: 10px;
    font-size: 18px;
    font-weight: 900;
    color: #94A3B8;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(148, 163, 184, 0.18);
}

#SidebarCollapseButton:hover {
    color: #F5F3FF;
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(129, 140, 248, 0.35);
}

#SidebarCollapseFooter {
    min-height: 38px;
    max-height: 38px;
    padding: 0 12px;
    border-radius: 12px;
    text-align: left;
    font-size: 11px;
    font-weight: 750;
    color: #94A3B8;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(148, 163, 184, 0.14);
}

#SidebarCollapseFooter:hover {
    color: #F5F3FF;
    background: rgba(124, 58, 237, 0.12);
    border-color: rgba(129, 140, 248, 0.28);
}

#SidebarRailButton {
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    padding: 0;
    border-radius: 14px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(27, 20, 52, 0.98),
        stop:1 rgba(20, 18, 40, 0.98)
    );
    border: 1px solid rgba(129, 140, 248, 0.32);
}

#SidebarRailButton:hover {
    background: rgba(124, 58, 237, 0.22);
    border-color: rgba(34, 211, 238, 0.44);
}

#Sidebar[collapsed="true"] {
    border-right: 1px solid rgba(148, 163, 184, 0.12);
}

#TopbarThemeButton {
    min-width: 88px;
    max-width: 88px;
    padding: 0 10px;
}

#SidebarLogoCard[collapsedLogo="true"] {
    border-radius: 16px;
    padding: 0;
    margin: 0;
}

#SidebarLogoCard[collapsedLogo="true"] #SMMark {
    margin: 0 auto;
}

#Sidebar[compact="true"] #SidebarLogoCard,
#Sidebar[compact="true"] #SidebarProfileCard {
    border-radius: 16px;
}

#SidebarLogoCard[compact="true"],
#SidebarProfileCard[compact="true"] {
    border-radius: 16px;
    padding: 0;
    margin: 0;
}

#Sidebar[compact="true"] #SidebarNavButton {
    padding: 0;
    text-align: center;
}

#SidebarNavButton[compact="true"],
#Sidebar[compact="true"] #SidebarNavButton {
    min-width: 48px;
    max-width: 48px;
    min-height: 40px;
    max-height: 40px;
    padding: 0;
    text-align: center;
}

#DangerButton {
    color: #F4C7BC;
    border-color: rgba(160, 83, 67, 0.35);
}

/* Typography */
#PageTitle {
    color: #F5F3FF;
    font-size: 28px;
    font-weight: 950;
    letter-spacing: 0px;
}

#PageDescription,
#PanelText,
#MutedText,
#QuickActionText,
#InstanceMeta {
    color: #94A3B8;
    font-size: 12px;
}

#PanelTitle,
#SectionTitle {
    color: #F5F3FF;
    font-size: 18px;
    font-weight: 900;
}

#CardTitle,
#InstanceTitle,
#QuickActionTitle {
    color: #F5F3FF;
    font-size: 14px;
    font-weight: 850;
}

#OverviewStatValue,
#DownloadBigNumber,
#SettingsRamValue,
#HeroStatValue {
    color: #FFFFFF;
    font-weight: 950;
}

#OverviewStatLabel,
#HeroStatTitle,
#SmallBadge,
#StatusBadge,
#InstanceBadge,
#ModTag {
    color: #C2CADB;
    background-color: rgba(124, 58, 237, 0.16);
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 7px;
    padding: 3px 8px;
    font-size: 10px;
    font-weight: 800;
}

/* Minecraft hero: keep game identity, remove sci-fi neon */
#MinecraftHero {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(13, 23, 17, 0.96),
        stop:0.55 rgba(13, 18, 19, 0.96),
        stop:1 rgba(31, 38, 26, 0.96)
    );
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 16px;
}

#HeroWelcome {
    color: #A5B4FC;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 1.4px;
}

#HeroTitle {
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 950;
}

#HeroSubtitle {
    color: #C9D4E4;
    font-size: 13px;
}

/* Progress */
QProgressBar,
#MiniProgress,
#BigProgress,
#DownloadProgress {
    background-color: rgba(8, 10, 20, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 5px;
    max-height: 8px;
}

QProgressBar::chunk,
#MiniProgress::chunk,
#BigProgress::chunk,
#DownloadProgress::chunk {
    background: #8B5CF6;
    border-radius: 5px;
}

/* Mod and icon boxes */
#ModIconBox,
#ModIconImage,
#ModDetailsIcon,
#OverviewIcon,
#QuickActionIcon,
#BlockIcon,
#DownloadIcon,
#HeroStatIcon {
    background-color: rgba(124, 58, 237, 0.16);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 10px;
}

#ModResultCard {
    border-radius: 14px;
    min-height: 150px;
}

/* Bottom status */
#BottomStatusBar {
    background-color: rgba(8, 10, 20, 0.92);
    border-top: 1px solid rgba(148, 163, 184, 0.12);
    min-height: 24px;
    max-height: 26px;
}
"""


LAUNCHER_SITE_MATCH_STYLE = r"""
/* SMLauncher — site-matched Minecraft dark skin
   Goal: make desktop launcher closer to website: calm dark panels, moss/stone green,
   less bright neon, more app-like cards. */

* {
    font-family: "Segoe UI";
    color: #F5F3FF;
}

QMainWindow {
    background-color: #0A0D18;
}

#AppContent {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0A0D18,
        stop:0.45 #0E1224,
        stop:1 #161C36
    );
}

/* calmer scrollbars */
QScrollBar:vertical {
    background: rgba(10, 13, 26, 165);
    width: 9px;
    border-radius: 4px;
    margin: 4px 2px 4px 2px;
}
QScrollBar::handle:vertical {
    background: rgba(139, 92, 246, 190);
    border-radius: 4px;
    min-height: 34px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(34, 211, 238, 220);
}
QScrollBar:horizontal {
    background: transparent;
    height: 0px;
}
QScrollBar::handle:horizontal {
    background: transparent;
    height: 0px;
}

/* sidebar closer to website header/preview */
#Sidebar {
    background: #070811;
    border-right: 1px solid rgba(148, 163, 184, 0.16);
}

#SidebarLogoCard {
    background: rgba(15, 18, 34, 0.96);
    border: 1px solid rgba(148, 163, 184, 0.26);
    border-radius: 18px;
}

#SMMark {
    background-color: rgba(23, 15, 41, 0.95);
    border: 1px solid rgba(68, 183, 96, 0.42);
    border-radius: 13px;
}

#SMLogoTitle {
    color: #F5F3FF;
    letter-spacing: 5px;
    font-size: 24px;
    font-weight: 950;
}

#SMLogoSubtitle,
#SidebarSectionTitle {
    color: #94A3B8;
    letter-spacing: 4px;
}

#SidebarNavButton {
    color: #E5E7EB;
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 850;
    padding: 0 12px;
}

#SidebarNavButton:hover {
    background-color: rgba(139, 92, 246, 0.14);
    border-color: rgba(148, 163, 184, 0.18);
}

#SidebarNavButton[active="true"] {
    color: #FFFFFF;
    background: #8B5CF6;
    border: 1px solid rgba(196, 181, 253, 0.26);
}

#SidebarProfileCard {
    background: rgba(15, 18, 34, 0.96);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 14px;
}

#SidebarProfileCard[active="true"] {
    background: rgba(139, 92, 246, 0.20);
    border-color: rgba(34, 211, 238, 0.40);
}

/* topbar */
#Topbar {
    background: rgba(10, 13, 26, 0.94);
    border-bottom: 1px solid rgba(148, 163, 184, 0.16);
}

#TopbarTitle {
    color: #F5F3FF;
    font-size: 18px;
    font-weight: 950;
}

#TopbarSubtitle {
    color: #94A3B8;
    font-size: 11px;
}

#CompactStatus {
    color: #A5B4FC;
    font-size: 11px;
    font-weight: 850;
    padding: 0 6px;
}

/* inputs */
QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
#TopbarSearch,
#SearchInput,
QLineEdit#Input {
    background-color: rgba(8, 10, 20, 0.86);
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-radius: 13px;
    color: #F5F3FF;
    padding: 8px 12px;
    font-size: 12px;
    min-height: 22px;
    selection-background-color: rgba(139, 92, 246, 0.55);
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus,
#TopbarSearch:focus,
#SearchInput:focus {
    background-color: rgba(10, 13, 26, 0.96);
    border-color: rgba(34, 211, 238, 0.52);
}

/* buttons */
#PrimaryButton,
#HeroPlayButton,
#TopbarPlayButton {
    background: #8B5CF6;
    color: #FFFFFF;
    border: 1px solid rgba(196, 181, 253, 0.26);
    border-radius: 13px;
    padding: 8px 15px;
    font-size: 12px;
    font-weight: 900;
}

#PrimaryButton:hover,
#HeroPlayButton:hover,
#TopbarPlayButton:hover {
    background: #06B6D4;
    border-color: rgba(196, 181, 253, 0.40);
}

#SecondaryButton,
#GhostButton,
#SmallGhostButton,
#WideGhostButton,
#TopbarThemeButton,
#TopbarStatusButton,
#ToggleFiltersButton {
    background-color: rgba(12, 15, 30, 0.88);
    color: #F5F3FF;
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-radius: 13px;
    padding: 8px 13px;
    font-size: 12px;
    font-weight: 850;
}

#SecondaryButton:hover,
#GhostButton:hover,
#SmallGhostButton:hover,
#WideGhostButton:hover,
#TopbarThemeButton:hover,
#TopbarStatusButton:hover,
#ToggleFiltersButton:hover {
    background-color: rgba(139, 92, 246, 0.18);
    border-color: rgba(34, 211, 238, 0.42);
}

/* cards / panels */
QFrame#Card,
QFrame#Panel,
QFrame#DashboardPanel,
QFrame#MiniCard,
QFrame#SettingsOptionsBox,
QFrame#DownloadSummaryCard,
QFrame#InstanceCard,
QFrame#ModResultCard,
QFrame#DownloadTaskCard,
QFrame#DownloadTaskCardActive,
QFrame#HeroStatCard,
QFrame#SettingsStatCard,
QFrame#SkinCard,
QFrame#AccountRow,
QFrame#AccountRowActive,
QFrame#DetailInfoRow,
QFrame#QuickActionCard,
QFrame#OverviewStatCard,
QFrame#ActivityRow,
QFrame#RecommendationRow,
QFrame#InstanceDashboardRow,
QFrame#InstanceDashboardRowActive,
QWidget#InstanceCard,
QWidget#Card {
    background: rgba(15, 18, 34, 0.94);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 16px;
}

QFrame#Card:hover,
QFrame#Panel:hover,
QFrame#DashboardPanel:hover,
QFrame#MiniCard:hover,
QFrame#InstanceCard:hover,
QFrame#ModResultCard:hover,
QFrame#QuickActionCard:hover,
QFrame#OverviewStatCard:hover,
QFrame#InstanceDashboardRow:hover,
QFrame#InstanceDashboardRowActive:hover,
QWidget#InstanceCard:hover,
QWidget#Card:hover {
    background: rgba(20, 22, 44, 0.96);
    border-color: rgba(34, 211, 238, 0.36);
}

/* Modrinth page filters */
#ModsAdvancedFilters {
    background: rgba(15, 18, 34, 0.90);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
}

#MinecraftShortcutCard {
    text-align: left;
    background: rgba(15, 18, 34, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 14px;
    color: #E5E7EB;
    padding: 11px 13px;
    font-size: 12px;
    font-weight: 850;
}

#MinecraftShortcutCard:hover {
    background: rgba(139, 92, 246, 0.16);
    border-color: rgba(34, 211, 238, 0.38);
}

#ModResultCard {
    background: rgba(10, 16, 26, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 16px;
}

#ModResultCard:hover {
    background: rgba(12, 20, 29, 0.92);
    border-color: rgba(34, 211, 238, 0.40);
}

#StatusBadge,
#SmallBadge,
#InstanceBadge,
#ModTag {
    color: #D9DFF0;
    background-color: rgba(139, 92, 246, 0.18);
    border: 1px solid rgba(34, 211, 238, 0.26);
    border-radius: 8px;
    padding: 3px 8px;
    font-size: 10px;
    font-weight: 850;
}

#PageTitle {
    color: #F5F3FF;
    font-size: 28px;
    font-weight: 950;
}

#PageDescription,
#PanelText,
#MutedText,
#QuickActionText,
#InstanceMeta {
    color: #94A3B8;
}

#PanelTitle,
#SectionTitle,
#CardTitle,
#InstanceTitle,
#QuickActionTitle {
    color: #F5F3FF;
    font-weight: 900;
}

/* hero */
#MinecraftHero {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(15, 18, 34, 0.96),
        stop:0.52 rgba(11, 13, 27, 0.94),
        stop:1 rgba(16, 24, 32, 0.94)
    );
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-radius: 18px;
}

#HeroWelcome {
    color: #A5B4FC;
}

#HeroTitle {
    color: #F5F3FF;
}

QProgressBar,
#MiniProgress,
#BigProgress,
#DownloadProgress {
    background-color: rgba(8, 10, 20, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 5px;
    max-height: 8px;
}

QProgressBar::chunk,
#MiniProgress::chunk,
#BigProgress::chunk,
#DownloadProgress::chunk {
    background: #8B5CF6;
    border-radius: 5px;
}

#BottomStatusBar {
    background: rgba(8, 10, 20, 0.96);
    border-top: 1px solid rgba(148, 163, 184, 0.14);
}
"""


CONTENT_SPLIT_AND_DARK_ONLY_STYLE = r"""
/* Content split tabs */
#ContentTypeTab {
    background-color: rgba(12, 15, 30, 0.88);
    color: #DFE5F4;
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-radius: 13px;
    padding: 9px 18px;
    font-size: 12px;
    font-weight: 900;
    min-height: 36px;
}

#ContentTypeTab:hover {
    background-color: rgba(139, 92, 246, 0.18);
    border-color: rgba(34, 211, 238, 0.42);
}

#ContentTypeTab[active="true"],
#ContentTypeTab:checked {
    color: #FFFFFF;
    background: #8B5CF6;
    border-color: rgba(196, 181, 253, 0.32);
}

/* Content area stays on the dark Minecraft palette in all themes. */
#AppContent,
QMainWindow {
    background-color: #0A0D18;
}

QLabel {
    color: #F5F3FF;
}

QFrame#ModResultCard QLabel,
QFrame#Card QLabel,
QFrame#Panel QLabel,
QFrame#DashboardPanel QLabel,
QFrame#MiniCard QLabel,
QFrame#SettingsOptionsBox QLabel,
QFrame#DownloadSummaryCard QLabel,
QFrame#InstanceCard QLabel,
QFrame#DownloadTaskCard QLabel,
QFrame#HeroStatCard QLabel,
QFrame#SettingsStatCard QLabel,
QFrame#SkinCard QLabel,
QFrame#AccountRow QLabel,
QFrame#DetailInfoRow QLabel,
QFrame#QuickActionCard QLabel,
QFrame#OverviewStatCard QLabel {
    color: #F5F3FF;
}

QFrame#ModResultCard #PanelText,
QFrame#ModResultCard #InstanceMeta,
#PanelText,
#InstanceMeta,
#MutedText,
#PageDescription {
    color: #94A3B8;
}
"""


SIDEBAR_LOGO_SAFE_STYLE = r"""
/* Fix for clipped launcher title in sidebar logo card */
#SidebarLogoCard {
    min-height: 88px;
    border-radius: 18px;
}

#SMMark {
    min-width: 56px;
    max-width: 56px;
    min-height: 56px;
    max-height: 56px;
    border-radius: 13px;
}

#SMLogoTitle {
    color: #F5F3FF;
    font-size: 22px;
    font-weight: 950;
    letter-spacing: 3px;
    padding: 0px;
    margin: 0px;
    background: transparent;
}

#SMLogoSubtitle {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 850;
    letter-spacing: 3px;
    padding: 0px;
    margin: 0px;
    background: transparent;
}
"""


OVERHAUL_POLISH_STYLE = r"""
/* Overhaul polish: tighter catalog and clearer dark Minecraft UI */
#ModsAdvancedFilters {
    border-radius: 18px;
    background-color: rgba(10, 13, 24, 0.88);
    border: 1px solid rgba(129, 140, 248, 0.22);
}

#MinecraftShortcutCard {
    min-height: 38px;
    padding: 8px 12px;
    border-radius: 12px;
    font-size: 11px;
}

#ContentTypeTab {
    min-width: 78px;
    min-height: 36px;
    padding: 8px 18px;
}

#ModResultCard {
    border-radius: 16px;
    background-color: rgba(11, 14, 28, 0.92);
}

#ModResultCard:hover {
    background-color: rgba(12, 20, 15, 0.96);
    border-color: rgba(114, 162, 79, 0.45);
}

#ToggleFiltersButton {
    min-width: 130px;
}

#TopbarStatusButton {
    min-width: 96px;
}

QLineEdit {
    selection-background-color: #7C3AED;
}

/* Make bottom/status bar a bit more launcher-like */
#BottomStatusBar {
    background-color: rgba(7, 8, 16, 0.90);
    border-top: 1px solid rgba(148, 163, 184, 0.20);
}
"""



CALM_COMPACT_STYLE = r"""
/* Calm compact launcher refresh */
* {
    font-size: 12px;
}

QMainWindow {
    background-color: #0E1120;
}

#AppContent {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #121629, stop:0.55 #181C34, stop:1 #10142A);
}

#Sidebar {
    background-color: #0F1324;
    border-right: 1px solid rgba(196, 205, 195, 0.10);
}

#SidebarLogoCard,
#SidebarProfileCard,
QFrame#DashboardPanel,
QFrame#Panel,
QFrame#Card,
QFrame#MiniCard,
QFrame#DownloadSummaryCard,
QFrame#InstanceCard,
QFrame#ModResultCard,
QFrame#DownloadTaskCard,
QFrame#HeroStatCard,
QFrame#QuickActionCard,
QFrame#OverviewStatCard,
QFrame#ActivityRow,
QFrame#RecommendationRow,
#CalmHero,
#HeroInfoChip {
    background-color: rgba(28, 26, 54, 0.96);
    border: 1px solid rgba(210, 220, 210, 0.09);
    border-radius: 18px;
}

QFrame#InstanceDashboardRow,
QFrame#InstanceDashboardRowActive {
    background-color: rgba(14, 20, 17, 0.98);
    border: 1px solid rgba(129, 140, 248, 0.24);
    border-radius: 14px;
    min-height: 58px;
}

QFrame#InstanceDashboardRow #InstanceTitle,
QFrame#InstanceDashboardRowActive #InstanceTitle {
    color: #F2F5FC;
}

QFrame#InstanceDashboardRow #InstanceMeta,
QFrame#InstanceDashboardRowActive #InstanceMeta {
    color: #A6B2C6;
}

#SidebarLogoCard,
#SidebarProfileCard {
    background-color: rgba(22, 28, 24, 0.98);
    border-radius: 16px;
}

#CalmHero {
    border-radius: 22px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(34, 28, 64, 0.98), stop:1 rgba(22, 20, 46, 0.98));
}

#HeroInfoChip {
    min-width: 0px;
    max-width: 280px;
}

#SidebarNavButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 14px;
    padding: 0 14px;
    font-size: 13px;
    font-weight: 700;
    color: #E0E6F2;
}

#SidebarNavButton:hover {
    background-color: rgba(129, 140, 248, 0.10);
    border-color: rgba(129, 140, 248, 0.20);
}

#SidebarNavButton[active="true"] {
    background-color: rgba(129, 140, 248, 0.18);
    border-color: rgba(129, 140, 248, 0.32);
    color: #F2F5FC;
}

#SMLogoTitle {
    font-size: 21px;
    letter-spacing: 2px;
}

#SMLogoSubtitle,
#SidebarSectionTitle,
#TopbarSubtitle,
#OverviewStatLabel,
#HeroStatTitle,
#InstanceMeta,
#OverviewStatMeta,
#ActivityMeta,
#QuickActionText,
#PanelText,
#PageDescription,
#MutedText,
#EmptyText,
#BottomStatusText {
    color: #A6B2C6;
}

#SidebarSectionTitle {
    letter-spacing: 2px;
    padding-left: 6px;
}

#SidebarProfileName,
#TopbarTitle,
#PanelTitle,
#CardTitle,
#InstanceTitle,
#HeroTitle,
#OverviewStatValue,
#HeroStatValue,
#DownloadBigNumber,
#PageTitle {
    color: #F2F5FC;
}

#SidebarProfileStatus {
    color: #9FB2D0;
}

#Topbar {
    background-color: rgba(17, 18, 36, 0.90);
    border-bottom: 1px solid rgba(210, 220, 210, 0.08);
}

#TopbarTitle {
    font-size: 18px;
}

#TopbarSearch,
#SearchInput,
QLineEdit#Input,
QLineEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QTextEdit,
QPlainTextEdit {
    background-color: rgba(18, 19, 38, 0.95);
    border: 1px solid rgba(210, 220, 210, 0.10);
    border-radius: 13px;
    padding: 9px 12px;
    color: #F2F5FC;
}

#TopbarPlayButton,
#HeroPlayButton,
#PrimaryButton {
    background-color: #8B5CF6;
    border: 1px solid #22D3EE;
    border-radius: 13px;
    color: #12081F;
    padding: 10px 18px;
    font-weight: 800;
}

#TopbarPlayButton:hover,
#HeroPlayButton:hover,
#PrimaryButton:hover {
    background-color: #A5B4FC;
}

#SecondaryButton,
#SmallGhostButton,
#WideGhostButton,
#GhostButton,
#TopbarThemeButton,
#ToggleFiltersButton {
    background-color: rgba(20, 21, 42, 0.98);
    border: 1px solid rgba(210, 220, 210, 0.10);
    border-radius: 13px;
    color: #E6EBF6;
    padding: 9px 14px;
    font-weight: 700;
}

#SecondaryButton:hover,
#SmallGhostButton:hover,
#WideGhostButton:hover,
#GhostButton:hover,
#TopbarThemeButton:hover,
#ToggleFiltersButton:hover {
    border-color: rgba(129, 140, 248, 0.30);
    background-color: rgba(29, 28, 58, 0.98);
}

#HeroTitle {
    font-size: 32px;
}

#HeroSubtitle {
    font-size: 13px;
    color: #DBE1EC;
}

#HeroWelcome {
    font-size: 12px;
    letter-spacing: 1px;
    color: #A6B2C6;
}

#StatusBadge,
#SmallBadge,
#InstanceBadge,
#ModTag {
    background-color: rgba(139, 92, 246, 0.14);
    border: 1px solid rgba(129, 140, 248, 0.18);
    color: #E9EEFA;
    border-radius: 10px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 700;
    max-width: 160px;
}

#OverviewStatCard,
#ActivityRow,
#RecommendationRow,
#InstanceDashboardRow,
#InstanceDashboardRowActive,
#HeroInfoChip {
    border-radius: 16px;
}

#OverviewStatValue {
    font-size: 22px;
}

#OverviewIcon,
#QuickActionIcon,
#BlockIcon,
#DownloadIcon,
#HeroStatIcon {
    background-color: rgba(139, 92, 246, 0.10);
    border: 1px solid rgba(129, 140, 248, 0.14);
    border-radius: 10px;
}

#MiniProgress,
#BigProgress,
#DownloadProgress,
QProgressBar {
    background: rgba(14, 15, 30, 0.90);
    border: 1px solid rgba(210, 220, 210, 0.06);
    border-radius: 999px;
    max-height: 6px;
}

#MiniProgress::chunk,
#BigProgress::chunk,
#DownloadProgress::chunk,
QProgressBar::chunk {
    background: #22D3EE;
    border-radius: 999px;
}

#BottomStatusBar {
    background-color: rgba(16, 17, 34, 0.96);
    border-top: 1px solid rgba(210, 220, 210, 0.08);
}
"""





DESIGN_TOKENS = {
    "background": "#0F1226",
    "surface": "#161B33",
    "elevated_surface": "#1E2440",
    "border": "#2E3654",
    "subtle_border": "#262E4A",
    "primary_text": "#F2F5FC",
    "secondary_text": "#B9C2D4",
    "muted_text": "#8B97AD",
    "accent": "#A78BFA",
    "success": "#67E8F9",
    "warning": "#F6AD55",
    "error": "#FCA5A5",
    "hover": "#262E4A",
    "pressed": "#33385E",
    "disabled": "#4E5A75",
}

DESIGN_METRICS = {
    "radius_small": 8, "radius_medium": 12, "radius_large": 20,
    "space_small": 8, "space_medium": 16, "space_large": 28,
    "control_height": 38, "body_size": 13, "section_size": 18, "page_size": 27,
}

THEME_TOKEN_OVERRIDES = {
    "amoled": {"background": "#06070F", "surface": "#10152A", "accent": "#A5B4FC",
               "hero_start": "#221743", "hero_end": "#120F26", "hero_border": "#3B2A6B"},
    "forest": {"accent": "#A5B4FC", "hero_start": "#2A1B45",
               "hero_end": "#1B1140", "hero_border": "#4C1D95"},
    "ocean": {"accent": "#7DD3FC", "hero_start": "#162A4A",
              "hero_end": "#101C36", "hero_border": "#2F6E8F"},
    "purple": {"accent": "#C4B5FD", "hero_start": "#342A42",
               "hero_end": "#201B2C", "hero_border": "#5C4B70"},
    "sunset": {"accent": "#F6AD55", "hero_start": "#433229",
               "hero_end": "#2A211D", "hero_border": "#705443"},
}

SM_2_STYLE = r"""
/* SMLauncher 2.0 shell and shared desktop foundations */
QMainWindow, #AppContent, #HomeContent { background-color: @background@; }
#Sidebar { background-color: #141228; border-right: 1px solid @subtle_border@; }
#SidebarLogoCard, #SidebarProfileCard {
    background: transparent; border: none; border-radius: 0;
}
#SMLogoTitle { color: @primary_text@; font-size: 17px; font-weight: 800; letter-spacing: 1px; }
#SMLogoSubtitle { color: @muted_text@; font-size: 11px; }
#SidebarNavButton {
    background: transparent; border: none; border-radius: 10px;
    color: @secondary_text@; font-size: 13px; font-weight: 600;
    text-align: left; padding-left: 16px; min-height: 42px;
}
#SidebarNavButton:hover { background: @hover@; color: @primary_text@; }
#SidebarNavButton[active="true"] {
    background: @pressed@; border: none; color: @primary_text@;
}
#SidebarNavButton[compact="true"] { padding-left: 0; text-align: center; }
#SidebarCollapseButton { background: transparent; border: none; border-radius: 8px; }
#SidebarCollapseButton:hover { background: @hover@; }
#Topbar {
    background-color: @background@; border-bottom: 1px solid @subtle_border@;
}
#TopbarTitle { color: @primary_text@; font-size: 15px; font-weight: 700; }
#TopbarDownloadsButton, #TopbarThemeButton, #TopbarAccountButton {
    background: transparent; border: none; border-radius: 9px;
    color: @secondary_text@; font-size: 12px; padding: 7px 10px;
}
#TopbarDownloadsButton:hover, #TopbarThemeButton:hover, #TopbarAccountButton:hover {
    background: @hover@; color: @primary_text@;
}
#PageTitle { color: @primary_text@; font-size: @page_size@px; font-weight: 700; }
#PageDescription, #PanelText, #MutedText { color: @secondary_text@; font-size: 13px; }
#PanelTitle { font-size: 18px; font-weight: 700; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
    background: @surface@; border: 1px solid @border@; border-radius: 10px;
    color: @primary_text@; padding: 8px 11px; font-size: 13px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: @accent@;
}
#PrimaryButton, #HeroPlayButton {
    background: @accent@; border: none; border-radius: @radius_medium@px;
    color: #0F0A1C; font-size: @body_size@px; font-weight: 800; padding: 10px 18px;
}
#PrimaryButton:hover, #HeroPlayButton:hover { background: #C4B5FD; }
#PrimaryButton:pressed, #HeroPlayButton:pressed { background: #6D28D9; }
#HeroPlayButton:disabled { background: @disabled@; color: @secondary_text@; }
#SecondaryButton, #SmallGhostButton, #GhostButton, #WideGhostButton {
    background: @elevated_surface@; border: 1px solid @subtle_border@;
    border-radius: 10px; color: @primary_text@; padding: 9px 13px; font-size: 12px;
}
#SecondaryButton:hover, #SmallGhostButton:hover, #GhostButton:hover, #WideGhostButton:hover {
    background: @hover@; border-color: @border@;
}
QFrame#DashboardPanel, QFrame#Panel, QFrame#Card, QFrame#MiniCard,
QFrame#DownloadSummaryCard, QFrame#InstanceCard, QFrame#ModResultCard,
QFrame#DownloadTaskCard, QFrame#HeroStatCard, QFrame#SettingsStatCard {
    background: @surface@; border: 1px solid @subtle_border@; border-radius: 14px;
}
QFrame#DashboardPanel:hover, QFrame#Panel:hover, QFrame#Card:hover,
QFrame#InstanceCard:hover, QFrame#ModResultCard:hover {
    background: @elevated_surface@; border-color: @border@;
}
#HomeEyebrow { color: @muted_text@; font-size: 11px; font-weight: 700; letter-spacing: 1px; }
#HomeHeading { color: @primary_text@; font-size: 27px; font-weight: 700; }
#HomeEmpty { background: @surface@; border: 1px solid @subtle_border@; border-radius: 20px; }
#HomeEmptyTitle { color: @primary_text@; font-size: 24px; font-weight: 700; }
#HomeMuted { color: @secondary_text@; font-size: 13px; }
#HomeInstancePicker { min-height: 36px; }
#LaunchHero {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 @hero_start@, stop:0.52 @hero_mid@, stop:1 @hero_end@);
    border: 1px solid @hero_border@; border-radius: 22px; min-height: 330px;
}
#HeroKicker { color: @accent@; font-size: 11px; font-weight: 800; letter-spacing: 1px; }
#LaunchHeroTitle { color: @primary_text@; font-size: 35px; font-weight: 800; }
#LaunchHeroMeta { color: #C7D2FE; font-size: 15px; }
#LaunchStateTitle { color: @primary_text@; font-size: 14px; font-weight: 700; }
#HomeDetails { background: @surface@; border: none; border-radius: 12px; }
#HomeDetailValue { color: @primary_text@; font-size: 14px; font-weight: 600; }
QScrollBar:vertical { background: transparent; width: 8px; border: none; }
QScrollBar::handle:vertical { background: @border@; border-radius: 4px; min-height: 32px; }
"""


def _sm_2_style(theme):
    style = SM_2_STYLE
    tokens = {
        **DESIGN_TOKENS,
        "hero_start": "#2A1B45", "hero_mid": "#241743",
        "hero_end": "#1B1140", "hero_border": "#4C1D95",
    }
    tokens.update(THEME_TOKEN_OVERRIDES.get(theme, {}))
    tokens.update(DESIGN_METRICS)
    for name, value in tokens.items():
        style = style.replace(f"@{name}@", str(value))
    return style


ACCOUNT_MENU_STYLE = """
/* Выпадающий список аккаунтов в топбаре */
QFrame#AccountDropdown {
    background-color: #0B1220;
    border: 1px solid #1E293B;
    border-radius: 14px;
}
#AccountDropdownTitle {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}
QFrame#AccountChip, QFrame#AccountChipActive, QFrame#AccountChoiceCard {
    background-color: rgba(15, 23, 42, 0.85);
    border: 1px solid #1E293B;
    border-radius: 12px;
}
QFrame#AccountChip:hover, QFrame#AccountChoiceCard:hover {
    border: 1px solid rgba(34, 211, 238, 0.35);
}
QFrame#AccountChipActive {
    background-color: rgba(13, 148, 136, 0.14);
    border: 1px solid rgba(34, 211, 238, 0.45);
}
#AccountChipName { color: #F1F5F9; font-size: 14px; font-weight: 700; }
#AccountChipMeta { color: #94A3B8; font-size: 11px; }
#SmallPrimaryButton {
    background-color: #0E7490;
    color: #F8FAFC;
    border: none;
    border-radius: 8px;
    padding: 0 12px;
    font-weight: 700;
}
#SmallPrimaryButton:hover { background-color: #0891B2; }
#SmallPrimaryButton:disabled { background-color: #164E63; color: #67E8F9; }
"""


ACCOUNT_SETUP_WINDOW_STYLE = """
/* Отдельное окно создания аккаунта (видео-фон) */
#AccountSetupWindow {
    background-color: #02040C;
}
#SetupVideoBackground {
    background-color: #02040C;
    border: none;
}
/* Затемнение видео: фон заметно темнее, чтобы UI читался */
#SetupVideoOverlay {
    background-color: rgba(2, 4, 12, 0.80);
}
#SetupContentCard {
    background-color: rgba(6, 11, 24, 0.94);
    border: 1px solid rgba(148, 163, 184, 0.32);
    border-radius: 24px;
}
#SetupContentCard #PageTitle {
    font-size: 30px;
}
/* Карточки-кнопки «Создать Offline аккаунт» / «Создать Ely.by аккаунт» */
#SetupContentCard QFrame#AccountChoiceCard {
    background-color: rgba(15, 23, 42, 0.96);
    border: 1px solid rgba(34, 211, 238, 0.40);
    border-radius: 18px;
}
#SetupContentCard QFrame#AccountChoiceCard:hover {
    background-color: rgba(124, 58, 237, 0.32);
    border: 1px solid rgba(34, 211, 238, 0.75);
}
#SetupContentCard QFrame#AccountChoiceCard #CardTitle {
    font-size: 17px;
}
#SetupContentCard QFrame#AccountChoiceCard #SmallBadge {
    background-color: rgba(34, 211, 238, 0.18);
    border: 1px solid rgba(34, 211, 238, 0.40);
}
/* Кнопка отключения звука видео — заметная, слева внизу */
#SetupMuteButton {
    background-color: rgba(6, 11, 24, 0.94);
    border: 1px solid rgba(34, 211, 238, 0.50);
    border-radius: 14px;
    color: #F1F5F9;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 800;
}
#SetupMuteButton:hover {
    background-color: rgba(124, 58, 237, 0.38);
    border-color: rgba(34, 211, 238, 0.80);
}
#SetupCloseButton {
    background-color: rgba(6, 11, 24, 0.94);
    border: 1px solid rgba(148, 163, 184, 0.38);
    border-radius: 12px;
    color: #E2E8F0;
    font-size: 15px;
    font-weight: 900;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    padding: 0;
}
#SetupCloseButton:hover {
    background-color: rgba(127, 29, 29, 0.75);
    border-color: rgba(248, 113, 113, 0.65);
    color: #FECACA;
}
"""


def get_app_style(theme=None):
    theme = (theme or _read_saved_theme() or "dark").lower()

    if theme == "light":
        theme = "dark"

    base = APP_STYLE + COMFORT_STYLE + MINECRAFT_CLEAN_STYLE + LAUNCHER_SITE_MATCH_STYLE + CONTENT_SPLIT_AND_DARK_ONLY_STYLE + SIDEBAR_LOGO_SAFE_STYLE + OVERHAUL_POLISH_STYLE + CALM_COMPACT_STYLE + ACCOUNT_MENU_STYLE + ACCOUNT_SETUP_WINDOW_STYLE

    themes = {
        "amoled": AMOLED_STYLE, "forest": FOREST_STYLE,
        "ocean": OCEAN_STYLE, "purple": PURPLE_STYLE,
        "sunset": SUNSET_STYLE,
    }
    return base + themes.get(theme, DARK_STYLE) + _sm_2_style(theme)
