!include "MUI2.nsh"
!include "LogicLib.nsh"

; Basic Information
Name "Full Screen Track"
OutFile "..\FullScreenTrackSetup.exe"
InstallDir "$LOCALAPPDATA\FullScreenTrack"

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Define warning message
!define MUI_DIRECTORYPAGE_TEXT_TOP "Warning: This software requires significant disk space. Please ensure sufficient storage and regularly clean up recorded files."

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    
    ; Copy program files
    File /r "..\dist\ScreenTrack\*.*"  
    
    ; Create required directories
    CreateDirectory "$INSTDIR\db"
    CreateDirectory "$INSTDIR\log"
    CreateDirectory "$INSTDIR\recordings"
    
    ; Create shortcuts
    SetShellVarContext current             
    CreateDirectory "$SMPROGRAMS\FullScreenTrack"
    CreateShortcut "$SMPROGRAMS\FullScreenTrack\FullScreenTrack.lnk" "$INSTDIR\ScreenTrack.exe"
    CreateShortcut "$DESKTOP\FullScreenTrack.lnk" "$INSTDIR\ScreenTrack.exe"
    CreateShortcut "$SMPROGRAMS\FullScreenTrack\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Write uninstall information
    WriteUninstaller "$INSTDIR\uninstall.exe"
    ; CURRENT_USER
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FullScreenTrack" \
                     "DisplayName" "Full Screen Track"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FullScreenTrack" \
                     "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FullScreenTrack" \
                     "DisplayIcon" "$INSTDIR\FullScreenTrack.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FullScreenTrack" \
                     "Publisher" "Your Company Name"
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FullScreenTrack" \
                       "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FullScreenTrack" \
                       "NoRepair" 1
SectionEnd

Section "Uninstall"
    ; Remove program files and directories
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\FullScreenTrack\FullScreenTrack.lnk"
    Delete "$SMPROGRAMS\FullScreenTrack\Uninstall.lnk"
    Delete "$DESKTOP\FullScreenTrack.lnk"
    RMDir "$SMPROGRAMS\FullScreenTrack"
    
    ; Remove registry entries from CURRENT_USER
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FullScreenTrack"
SectionEnd
