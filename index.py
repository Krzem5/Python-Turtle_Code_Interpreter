from tkinter import *
import re
import time
import tkinter.filedialog as fd
import tkinter.messagebox as box



def convert_code(txt):
    global l,idx,func,errs
    all_=txt.split('\n')
    c,l,idx,func,errs,vars_=[],0,-1,{},[],{}
    def match(seq):
        def clear_row(seq,l):return (l==0) or seq[:l]=='\t'*l
        global l,idx,func,errs
        try:
            if re.compile("}(\s|$)").match(seq[l-1:]) and clear_row(seq,l-1):
                l-=1
                if l==-1:raise Exception(f'indent;{idx+1};{l*4})')
                return -1
            elif re.compile("for ([a-z0-9_]+) in ([0-9]+):{(\s|$)").match(seq[l:]) and clear_row(seq,l):
                s,c_,c__,l=int(seq[l:].split(' ')[3].replace(':{','')),[],[],l+1
                while True:
                    idx+=1
                    seq_=match(all_[idx])
                    if seq_==-1:break
                    elif type(seq_) is list:c_.extend(seq_)
                for _ in range(s):c__.extend(c_)
                return c__
            elif re.compile("def ([a-z0-9_]+):{(\s|$)").match(seq[l:]) and clear_row(seq,l):
                l,name=l+1,seq[l+4:len(seq)-2]
                func[name]=[]
                while True:
                    idx+=1
                    seq_=match(all_[idx])
                    if seq_==-1:break
                    elif type(seq_) is list:func[name].extend(seq_)
                return 0
            elif (re.compile("#").match(seq[l:]) or seq=='') and clear_row(seq,l):return 0
            elif re.compile("(.+)(\s|$)").match(seq[l+7:].lower()) and seq[l:l+6]=='print(' and seq.endswith(')') and clear_row(seq,l):return ['pri'+seq[l+6:len(seq)-1]]
            elif re.compile("([0-9]+)(\s|$)").match(seq[l+9:].lower()) and seq[l:l+8]=='forward(' and seq.endswith(')') and clear_row(seq,l):return ['u'+seq[l+8:len(seq)-1]]
            elif re.compile("([0-9]+)(\s|$)").match(seq[l+6:].lower()) and seq[l:l+5]=='back(' and seq.endswith(')') and clear_row(seq,l):return ['d'+seq[l+5:len(seq)-1]]
            elif re.compile("([0-9]+)(\s|$)").match(seq[l+7:].lower()) and seq[l:l+6]=='right(' and seq.endswith(')') and clear_row(seq,l):return ['r'+seq[l+6:len(seq)-1]]
            elif re.compile("([0-9]+)(\s|$)").match(seq[l+6:].lower()) and seq[l:l+5]=='left(' and seq.endswith(')') and clear_row(seq,l):return ['l'+seq[l+5:len(seq)-1]]
            elif re.compile("([0-9]+)(\s|$)").match(seq[l+12:].lower()) and seq[l:l+11]=='turn_right(' and seq.endswith(')') and clear_row(seq,l):return ['tr'+str((int(seq[l+11:len(seq)-1])%360))]
            elif re.compile("([0-9]+)(\s|$)").match(seq[l+11:].lower()) and seq[l:l+10]=='turn_left(' and seq.endswith(')') and clear_row(seq,l):return ['tl'+str((int(seq[l+10:len(seq)-1])%360))]
            elif seq[l:]=='penup()' and clear_row(seq,l):return ['pu']
            elif seq[l:]=='pendown()' and clear_row(seq,l):return ['pd']
            elif ((re.compile("([a-f0-9]{6,6})(\s|$)").match(seq[l:l+11].lower()) and seq[l:l+10]=='pencolor(#' and seq.endswith(')')) or seq[l:]=='pencolor(reset)') and clear_row(seq,l):return ['pc'+seq[l+9:len(seq)-1]]
            elif ((re.compile("([a-f0-9]{6,6})(\s|$)").match(seq[l:l+10].lower()) and seq[l:l+9]=='bgcolor(#' and seq.endswith(')')) or seq[l:]=='bgcolor(reset)') and clear_row(seq,l):return ['bgc'+seq[l+8:len(seq)-1]]
            elif re.compile("([0-9]{1,1})(\s|$)").match(seq[l+7:].lower()) and seq[l:l+6]=='speed(' and seq.endswith(')') and clear_row(seq,l):return ['spd'+seq[l+6:len(seq)-1]]
            elif re.compile("([0-9]{1,4}),([0-9]{1,3})(\s|$)").match(seq[l+9:].lower()) and seq[l:l+8]=='sethome(' and seq.endswith(')') and clear_row(seq,l):return ['sh'+seq[l+8:len(seq)-1]]
            elif seq[l:]=='home()' and clear_row(seq,l):return ['h']
            elif ((re.compile("([a-z0-9_.]+)(\s|$)").match(seq[l+8:].lower()) and seq[l:l+7]=='sprite(' and seq.endswith(')')) or seq[l:]=='sprite(reset)') and clear_row(seq,l):return ['spr'+seq[l+7:len(seq)-1]]
            elif seq[l:]=='stamp()' and clear_row(seq,l):return ['stm']
            elif re.compile("([a-z0-9_.]+)(\s|$)").match(seq[l:].lower()) and seq[l:l+6]=='image(' and seq.endswith(')') and clear_row(seq,l):return ['img'+seq[l+6:len(seq)-1]]
            elif seq[l:]=='help()' and clear_row(seq,l):return ['help']
            else:
                found_f=False
                for f in list(func.keys()):
                    if not found_f:
                        if seq[l:].lower().endswith(f'{f}()') and clear_row(seq,l):
                            found_f=True
                            return func[f]
                def num_var(seq):
                    return re.compile('([a-z0-9_%-]+)').match(seq.lower())
                found_v,old_str=False,'.'.join(seq)
                old_str.replace('.','')
                seq=seq.replace(' ','')
                if re.compile('([a-z0-9_%]+)').match(seq.split('=')[0].lower()) and '=' in seq:vars_[seq.split('=')[0]]=0
                def replace_vars(seq):
                    string_var,swap_dict,var_letters,nseq=None,{},'abcdefghijklmnopqrstuvwxyz_',[]
                    if seq.isalpha():seq=str(vars_[seq])
                    elif seq.isnumeric():seq=str(seq)
                    else:
                        seq+='@'
                        nseq=list(seq)
                        for i in range(len(seq)):
                            char=seq[i]
                            if char.lower() in var_letters and string_var==None:string_var=[i,i]
                            elif char.lower() in var_letters and type(string_var)==list:string_var=[string_var[0],i]
                            elif char.lower() not in var_letters and type(string_var)==list:
                                nvar=time.time()
                                swap_dict[float((str(nvar)*((string_var[1]+1)-string_var[0])))]=vars_[seq[string_var[0]:(string_var[1]+1)]]
                                for idx_ in range(string_var[0],string_var[1]+1):nseq[idx_]=str(nvar)
                                string_var=None
                        nseq.remove("@")
                        seq=''.join(nseq)
                        for k in list(swap_dict.keys()):
                            seq=seq.replace(str(k),str(swap_dict[k]))
                    return seq
                for v in list(vars_.keys()):
                    if not found_v:
                        if '+=' in seq:
                            if seq[l:].startswith(f"{v}+=") and clear_row(seq,l):
                                found_v=True
                                return [f"setv {v},{v} + {eval(replace_vars(seq[l:].split('+=')[1]))}"]
                        elif '-=' in seq:
                            if seq[l:].startswith(f"{v}-=") and clear_row(seq,l):
                                found_v=True
                                return [f"setv {v},{v} + {eval(replace_vars(seq[l:].split('-=')[1]))}"]
                        elif '**=' in seq:
                            if seq[l:].startswith(f"{v}**=") and clear_row(seq,l):
                                found_v=True
                                return [f"setv {v},{v} ** {eval(replace_vars(seq[l:].split('**=')[1]))}"]
                        elif '//=' in seq:
                            if seq[l:].startswith(f"{v}//=") and clear_row(seq,l):
                                found_v=True
                                return [f"setv {v},{v} // {eval(replace_vars(seq[l:].split('//=')[1]))}"]
                        elif '*=' in seq:
                            if seq[l:].startswith(f"{v}*=") and clear_row(seq,l):
                                found_v=True
                                return [f"setv {v},{v} + {eval(replace_vars(seq[l:].split('*=')[1]))}"]
                        elif '/=' in seq:
                            if seq[l:].startswith(f"{v}/=") and clear_row(seq,l):
                                found_v=True
                                return [f"setv {v},{v} + {eval(replace_vars(seq[l:].split('/=')[1]))}"]
                seq=str(old_str.replace('.',''))
                del old_str
                if re.compile("([a-z0-9_]+)=(.+)(\s|$)").match(seq[l:].lower()) and clear_row(seq,l):
                    try:
                        vars_[seq[l:].split('=')[0]]=eval(replace_vars(seq[l:].split('=')[1]))
                    except:
                        raise Exception(f"math;{idx+1};{l*4}")
                    return [f"setv {seq[l:].split('=')[0]} = {eval(replace_vars(seq[l:].split('=')[1]))}"]
            raise Exception(f"syntax;{idx+1};{l*4}")
        except Exception as ex:
            if errs==[]:errs=str(ex).split(';')
    while not idx==len(all_)-1:
        idx+=1
        seq_=match(all_[idx])
        if type(seq_) is list:c.extend(seq_)
    if errs!=[]:return errs,True
    else:return c,False
def close(arg):
    global savedfile,openfilename
    if not savedfile:
        if box.askyesno('Save File',f'Save file {openfilename} before closing?')==1:
            with open(f'{openfilename}.txt','w') as f:
                f.write(code_txtb.get('1.0','end'))       
    tk.destroy()
    quit()
def insert(seq,enter=None):
    print('-',enter,'-',seq)
    if type(enter)==int:seq+=' '*(125-enter%125)
    shell['state']='normal'
    shell.insert('end',seq)
    shell['state']='disabled'
def insert_(seq,total_str_len):
    idx_enter_cnt=0
    for s in seq.replace('\\t','    ').split('\\n'):
        if idx_enter_cnt<len(seq.split('\\n'))-1:
            idx_enter_cnt+=1
            print((125-len(s))%125,s)
            insert(s,enter=(125-len(s))%125)
        total_str_len+=len(s)
    return total_str_len
def restart_shell(arg):
    global resseted
    shell['state']='normal'
    shell.delete('1.0','end')
    shell['state']='disabled'
    resseted=True
    insert("""                                                    +----------------+
                                                    |     TURTLE®    |
                                                    +----------------+
=============================================================================================================================""")
def shell_reset():
    global resseted,restartcnt
    if not resseted:
        seq=f'RESTART #{restartcnt}'.center(125,'=')
        insert(f"\n{seq}")
        restartcnt+=1
    resseted=False
def home(pos,pos2):
    return pos2
def move(d,distance,pos):
    return pos
def turn(d,degrees,facing):
    return facing
def stamp(pos):
    pass
def run(arg):
    global help_txt
    shell_reset()
    l=convert_code(code_txtb.get('1.0','end'))
    if l[1]:insert(f"{l[0][0].capitalize()}Error in line {l[0][1]}, column {l[0][2]}.")
    else:
        facing,x,y,pendown,penc,bgc,home,speed,vars_=0,0,0,False,'#000000','#FFFFFF',[0,0],0,{}
        def remove_vars(seq):
            seq=seq.replace('%vars',str([f"{v}={vars_[v]}" for v in list(vars_.keys())])).replace('%x',str(x)).replace('%y',str(y)).replace('%facing',str(facing)).replace('%pendown',str(pendown)).replace('%pencolor',str(penc)).replace('%bgcolor',str(bgc)).replace('%homex',str(home[0])).replace('%homey',str(home[1])).replace('%speed',str(speed)).replace('%all',f'pos=<{str(x)},{str(y)}> facing={str(facing)} pendown={str(pendown)} pencolor={str(penc)} bgcolor={str(bgc)}  home=<{str(home[0])},{str(home[1])}> speed={str(speed)} vars={[f"{v}={vars_[v]}" for v in list(vars_.keys())]}')
            for v in list(vars_.keys()):seq=seq.replace(v,str(vars_[v]))
            return seq
        for seq in l[0]:
            old_seq=str(seq)
            seq=remove_vars(seq)
            if seq.startswith('pri'):
                l_,total_str_len=old_seq[3:].split(','),0
                for l in l_:
                    if l.startswith('"') and l.endswith('"'):
                        total_str_len=insert_(l.replace('"',''),total_str_len)
                    elif '%' in l:
                        total_str_len=insert_(l.replace('%vars',str([f"{v}={vars_[v]}" for v in list(vars_.keys())])).replace('%x',str(x)).replace('%y',str(y)).replace('%facing',str(facing)).replace('%pendown',str(pendown)).replace('%pencolor',str(penc)).replace('%bgcolor',str(bgc)).replace('%homex',str(home[0])).replace('%homey',str(home[1])).replace('%speed',str(speed)).replace('%all',f'pos=<{str(x)},{str(y)}> facing={str(facing)} pendown={str(pendown)} pencolor={str(penc)} bgcolor={str(bgc)}  home=<{str(home[0])},{str(home[1])}> speed={str(speed)} vars={[f"{v}={vars_[v]}" for v in list(vars_.keys())]}'),total_str_len)
                    else:
                        for v in list(vars_.keys()):l=l.replace(v,str(vars_[v]))
                        total_str_len=insert_(l,total_str_len)
                insert('',enter=total_str_len)
            elif seq.startswith('fd'):x,y=move('forward',int(seq[2:]),[x,y])
            elif seq.startswith('b'):x,y=move('back',int(seq[1:]),[x,y])
            elif seq.startswith('r'):x,y=move('right',int(seq[1:]),[x,y])
            elif seq.startswith('l'):x,y=move('left',int(seq[1:]),[x,y])
            elif seq.startswith('tr'):facing=turn('right',int(seq[2:]),facing)
            elif seq.startswith('tl'):facing=turn('left',int(seq[2:]),facing)
            elif seq.startswith('pu'):pendown=False
            elif seq.startswith('pd'):pendown=True
            elif seq.startswith('pc'):
                if seq[2:]=='reset':penc='#000000'
                else:penc=seq[2:]
            elif seq.startswith('bgc'):
                if seq[3:]=='reset':canvas['bg']='#FFFFFF'
                else:canvas['bg']=seq[3:]
            elif seq.startswith('spd'):speed=int(seq[2:])
            elif seq.startswith('sh'):home=[int(seq[2:].split(',')[0]),int(seq[2:].split(',')[1])]
            elif seq=='h':x,y=home([x,y],home)
            elif seq.startswith('spr'):insert(seq[3:])
            elif seq.startswith('stm'):stamp([x,y])
            elif seq.startswith('img'):insert(seq[3:])
            elif seq.startswith('setv'):
                if ' = ' in seq:vars_[seq[5:].split(' = ')[0]]=int(seq[5:].split(' = ')[1])
                elif ' + ' in seq:vars_[old_seq[5:].split(',')[0]]=int(seq[5:].split(',')[1].split(' + ')[0])+int(seq[5:].split(',')[1].split(' + ')[1])
                elif ' - ' in seq:vars_[old_seq[5:].split(',')[0]]=int(seq[5:].split(',')[1].split(' - ')[0])-int(seq[5:].split(',')[1].split(' - ')[1])
                elif ' * ' in seq:vars_[old_seq[5:].split(',')[0]]=int(seq[5:].split(',')[1].split(' * ')[0])*int(seq[5:].split(',')[1].split(' * ')[1])
                elif ' / ' in seq:vars_[old_seq[5:].split(',')[0]]=int(seq[5:].split(',')[1].split(' / ')[0])/int(seq[5:].split(',')[1].split(' / ')[1])
                elif ' ** ' in seq:vars_[old_seq[5:].split(',')[0]]=int(seq[5:].split(',')[1].split(' ** ')[0])**int(seq[5:].split(',')[1].split(' ** ')[1])
                elif ' // ' in seq:vars_[old_seq[5:].split(',')[0]]=int(seq[5:].split(',')[1].split(' // ')[0])//int(seq[5:].split(',')[1].split(' // ')[1])
            elif seq=='help':insert(help_txt)
            bgc=canvas['bg']
def fullscreen(arg):
    global fsc,fsctk
    if fsc:fsctk.destroy()
    else:
        fsctk=Tk()
        fsctk.title(openfilename)
        fsctk['background']='white'
        fsctk.resizable(0,0)
        fsctk.minsize(width=100,height=100)
        fsctk.geometry('1910x1030+-5+-25')
        fsccv_fr=Frame(fsctk)
        fsccanvas=Canvas(fsccv_fr,bg='#FFFFFF',width=1000,height=753,borderwidth=1,highlightbackground='white',highlightthickness=0,highlightcolor='white')
        fsccv_fr.grid(row=0,column=0,sticky='nw')
        fsccanvas.grid(row=0,column=0)
        fsccanvas.bind_all('<F11>',func=fullscreen)
        canvas.bind_all('<F5>',func=run)
    fsc=not fsc
    
global openfilename,savedfile,fsc,resseted,restartcnt,help_txt
openfilename,savedfile,fsc,resseted,restartcnt,help_txt='Untitled',False,False,False,1,"""
=============================================================================================================================
                                            +-----------------------------------+
                                            |Help on Turtle® v1.0 win32 edition.|
                                            +-----------------------------------+
1) Introduction
    Turtle® is a simple programming launguage used to programm turtle's actions. It was born on (date) after
    ('2018-01-15'-date) days of work which was created using Python. Turtle® doesn't have many features.
    Here are some of them:
    - functions
    - 'for' loops
    - variables
    - basic drawing functions(move, go_to, pendown, color etc.)
    The 'Hello World! program looks like this:
    
    print 'Hello World!'

2) Commands

   command  |                                  description                                             |  usage example
 -----------+------------------------------------------------------------------------------------------+--------------------
 '#'        |After the '#' sign the rest of the line isn't going to matter while running the program.  | #comment
            |It's often used for notes.                                                                |
 -----------+------------------------------------------------------------------------------------------+--------------------
 '+'        |Add. (You don't need to space everything ex. a=10+b is the same as a = 10 + b this apply  | a = 10 + b
            |this to every single mathemathical equasion.)                                             |
 -----------+------------------------------------------------------------------------------------------+--------------------
 '-'        |Subtract.                                                                                 | a = 10 - b
 -----------+------------------------------------------------------------------------------------------+--------------------
 '*'        |Multiplication.                                                                           | a = 10 * b
 -----------+------------------------------------------------------------------------------------------+--------------------
 '/'        |Division.                                                                                 | a = 10 / b
 -----------+------------------------------------------------------------------------------------------+--------------------
 '**'       |Power.                                                                                    | a = 10 ** b
 -----------+------------------------------------------------------------------------------------------+--------------------
 '//'       |Floor division (division without a decimal point).                                        | a = 10 // b
 -----------+------------------------------------------------------------------------------------------+--------------------
 '='        |Equal.(TIP: You can use a operation character followed by a equal character to shorten    | a = 0
            |some code ex. 'a += 10' is the same as 'a = a + 10' etc.)                                 |
 -----------+------------------------------------------------------------------------------------------+--------------------
 'bgcolor'  |Sets the background color to a hex-typed color. (If you replace the color with the        | bgcolor('#000000')
            |word 'reset' background's color will be ressetd to white ex. 'bgcolor reset'.)            | bgcolor('reset')
 -----------+------------------------------------------------------------------------------------------+--------------------
 'pencolor' |Same as 'bgcolor' except it changes the pen color. (Tip is also the same)                 | pencolor('#FF0000')
 -----------+------------------------------------------------------------------------------------------+--------------------
 'def'      |Defines a function which can be called and executed.                                      | def func:{
            |                                                                                          |         print('a')
            |                                                                                          | }
            |                                                                                          | func()
 -----------+------------------------------------------------------------------------------------------+--------------------
 'for'      |Repeats a sample of code given number of times.                                           | for i in 4:{
            |                                                                                          |         print('a')
            |                                                                                          | }
 -----------+------------------------------------------------------------------------------------------+--------------------
 'forward'  |Moves turtle forword by a defined amount. Depends on turtle's facing direction.           | forward 6
 -----------+------------------------------------------------------------------------------------------+--------------------
 'back'     |Moves turtle back by a defined amount. Depends on turtle's facing direction.              | back 6
 -----------+------------------------------------------------------------------------------------------+--------------------
 'left'     |Moves turtle left by a defined amount. Depends on turtle's facing direction.              | left 6
 -----------+------------------------------------------------------------------------------------------+--------------------
 'right'    |Moves turtle right by a defined amount. Depends on turtle's facing direction.             | right 6
 -----------+------------------------------------------------------------------------------------------+--------------------
 'pendown'  |Makes a trial after the turtle.                                                           | pendown
 -----------+------------------------------------------------------------------------------------------+--------------------
 'penup'    |Opposite of 'pendown'.                                                                    | penup
 -----------+------------------------------------------------------------------------------------------+--------------------
 'help'     |Shows this document.                                                                      | help
 -----------+------------------------------------------------------------------------------------------+--------------------
 'home'     |Moves the turtle to it's home.                                                            | home
 -----------+------------------------------------------------------------------------------------------+--------------------
 'sethome'  |Sets turtle's home to a specific location.                                                | sethome 50,50  
 -----------+------------------------------------------------------------------------------------------+--------------------
 'speed'    |Changes turtle's movement speed. (0-fastest, 10-slowest)                                  | speed 3
 -----------+------------------------------------------------------------------------------------------+--------------------
 'sprite'   |Changes turtle's skin. Also affects 'stamp' command. (TIP: If you type 'reset' not        | sprite C:\sprite\sp
            |a sprite name, skin will be reseted to the originel one (basic turtle).)                  | sprite reset
 -----------+------------------------------------------------------------------------------------------+--------------------
 'turn_left'|Turn's turtle counterclockwise by a defined amount.                                       | turn_left 45 
 -----------+------------------------------------------------------------------------------------------+--------------------
 'turn_right|Turn's turtle clockwise by a defined amount.                                              | turn_right 45
 '          |                                                                                          |    
 -----------+------------------------------------------------------------------------------------------+--------------------
 'image'    |Creates a image at turtle's position.                                                     | image C:\images\img 
 -----------+------------------------------------------------------------------------------------------+--------------------
 'print'    |Prints a defined input. Input can contain 3 formats:                                      | print('x',x,%x)
            |- String (You can replace ' with ".)                                                      | print('x')
            |- Variable                                                                                | print(x)
            |- Buld-in turtle variable                                                                 | print(%x)
 -----------+------------------------------------------------------------------------------------------+--------------------
 'stamp'    |Creates turtle skin image at turtle's current location.                                   | stamp()
 -----------+------------------------------------------------------------------------------------------+--------------------
 
            |                                                                                          |

3) Geting turtle's data
    Lets say, that for example you want get turtle's x-position and save it to a variable. You could track turtle's
    x-position after every movement, but that is not very officiant. That's why there are build-in turtle variables.
    Here are some of them:
    %x - turtle's x position
    %y - turtle's y position
    %vars - all variables uesd in the script to the current point
    %facing - turtle's facing(clockwise starting at up position (0 degrees)
    %pencolor - turtle's pen color
    %bgcolor - background color
    %homex - turtle's home x position
    %homey - turtle's home y position
    %all - all build-in variables together
=============================================================================================================================
"""
fnc="""a=10**125
print(a,"\\nA")
"""
tk=Tk()
tk.title(openfilename)
tk['background']='white'
tk.resizable(0,0)
tk.minsize(width=100,height=100)
tk.geometry('1905x1005+0+0')
cv_fr=Frame(tk)
canvas=Canvas(cv_fr,bg='#FFFFFF',width=1000,height=753,borderwidth=1,highlightbackground='white',highlightthickness=0,highlightcolor='white')
cv_fr.grid(row=0,column=0,sticky='nw')
canvas.grid(row=0,column=0)
shell_fr=Frame(tk)
shell=Text(shell_fr,bg='#FFFFFF',borderwidth=0,highlightbackground='#000000',highlightthickness=2,highlightcolor='#000000',width=125,height=15,selectbackground='gray',selectborderwidth=0,selectforeground='black',state='disabled')
shell.grid(row=0,column=0)
shell_fr.grid(row=1,column=0,sticky='nw',columnspan=2)
txtb_fr=Frame(tk)
code_txtb=Text(txtb_fr,bg='#FFFFFF',tabs=32,borderwidth=0,highlightbackground='#000000',highlightthickness=2,highlightcolor='#000000',width=112,height=63,selectbackground='gray',selectborderwidth=0,selectforeground='black')
code_txtb.insert('end',fnc)
code_txtb.grid(row=0,column=0)
txtb_fr.grid(row=0,column=1,sticky='nw',rowspan=2)
canvas.bind_all('<Alt-F4>',func=close)
canvas.bind_all('<Control-r>',func=restart_shell)
canvas.bind_all('<F11>',func=fullscreen)
canvas.bind_all('<F5>',func=run)
restart_shell(None)

