# סימולטור CLI של סיסקו

סימולטור זה מדמה את ממשק שורת הפקודה (CLI) של מכשירי סיסקו, כולל נתבים ומתגים. הוא מאפשר למשתמשים לתרגל ולבחון פקודות סיסקו בסביבה מבוקרת.

## תכונות עיקריות

- ממשק CLI מדויק עם תחיליות מתאימות
- תמיכה במגוון רחב של פקודות סיסקו
- השלמת פקודות אוטומטית
- מצבי עבודה שונים (משתמש רגיל, מצב מיוחס, מצב קונפיגורציה, ועוד)
- תמיכה בשפות עברית ואנגלית
- היסטוריית פקודות
- טיפול בשגיאות והצעת תיקונים
- תמיכה בפקודות מורכבות כולל VLAN, ACL, DHCP, ניתוב סטטי, OSPF, ו-EIGRP

## דרישות מערכת

- Python 3.7 ומעלה
- SQLite3

## התקנה

1. שכפל את המאגר:
   ```
   git clone https://github.com/your-username/cisco-cli-simulator.git
   ```

2. עבור לתיקיית הפרויקט:
   ```
   cd cisco-cli-simulator
   ```

3. התקן את התלויות הנדרשות:
   ```
   pip install -r requirements.txt
   ```

## שימוש

להפעלת הסימולטור, הרץ את הפקודה הבאה מתוך תיקיית הפרויקט:

```
python main.py
```

בתחילת ההפעלה, תתבקש לבחור את סוג המכשיר (נתב או מתג) ואת השפה (עברית או אנגלית).

לאחר מכן, תוכל להזין פקודות סיסקו כרגיל. השתמש ב-`?` לקבלת עזרה ורשימת הפקודות הזמינות.

## דוגמאות לפקודות

- `enable` - כניסה למצב מיוחס
- `configure terminal` - כניסה למצב קונפיגורציה
- `show running-config` - הצגת הקונפיגורציה הנוכחית
- `interface GigabitEthernet0/0` - כניסה למצב קונפיגורציית ממשק
- `ip address 192.168.1.1 255.255.255.0` - הגדרת כתובת IP לממשק
- `show ip route` - הצגת טבלת הניתוב
- `vlan 10` - יצירת VLAN חדש
- `exit` - יציאה מהמצב הנוכחי

## פיתוח

הפרויקט מאורגן במספר מודולים עיקריים:

- `main.py`: נקודת הכניסה הראשית לסימולטור
- `cli_simulator.py`: מכיל את הלוגיקה העיקרית של הסימולטור
- `command_parser.py`: אחראי על ניתוח וביצוע הפקודות
- `data_manager.py`: מנהל את הנתונים ומצב המכשיר
- `logger.py`: מספק יכולות תיעוד

## בדיקות

להרצת בדיקות היחידה, השתמש בפקודה:

```
python -m unittest discover tests
```

## תרומה

אנו מעודדים תרומות לפרויקט! אנא צור issue או שלח pull request עם הצעות לשיפורים או תוספות.

## רישיון

פרויקט זה מופץ תחת רישיון MIT. ראה את קובץ `LICENSE` לפרטים נוספים.
