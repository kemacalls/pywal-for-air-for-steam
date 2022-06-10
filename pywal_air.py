"""
you must have "air for steam" and "pywal" installed to use this program.
it places a pywal template file in the correct place, refreshes pywal, 
tweaks the output, modifies air's config.ini, and creates a symlink 
so the skin will upgrade when you use pywal. 
run without args to begin.
"""
import sys
import os 
import shutil
import time 
import pyinputplus as pyp
import yaml
import argparse
from rich import print

user_home = os.path.expanduser('~')
yaml_defaults = {
    'first_run' : True,
    'config_file' : 'config.yaml',
    'config_path' : user_home + "/.config/pywal-steam-air/",
    'wal_template_path' : user_home + "/.config/wal/templates/",
    'wal_template_file' : '_pywal.styles',
    'wal_cache_path' : user_home + "/.cache/wal/",
    'steam_skins_path' : user_home + "/.steam/steam/skins/",
    'air_path' : "air-for-steam/Resource/themes/",
}

def main():
    # args
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-c", "--config", help="force setup", action="store_true")
    parser.add_argument("-t", "--template", help="force template file move", action="store_true")
    args = parser.parse_args()

    # config setup
    if not os.path.exists(yaml_defaults['config_path'] + yaml_defaults['config_file']):
        configSetup()
        yaml_config = yaml_defaults
    else:
        with open(yaml_defaults['config_path'] + yaml_defaults['config_file']) as config:
            yaml_config = yaml.safe_load(config)
            
    # user setup
    if yaml_config['first_run'] or args.config:
        userSetup(yaml_config)
        yaml_config['first_run'] = False
        with open(yaml_config['config_path'] + yaml_config['config_file'], 'w') as config:
            yaml.dump(yaml_config, config)
        print("[green]config file updated!")
        
    # move template
    if not os.path.exists(yaml_config['wal_template_path'] + yaml_config['wal_template_file']) or args.template:
        templateCopy(yaml_config)
    else:
        print('[yellow]found existing template...')

    # fix template output    
    commaFix(yaml_config)

    # make symlink
    if not os.path.exists(yaml_config['steam_skins_path'] + yaml_config['air_path'] + yaml_config['wal_template_file']):
        stylesSymlink(yaml_config)
    else:
        print('[yellow]found existing symlink for ' + yaml_config['wal_template_file'] + '...')
    
    # change air's config file
    airConfig(yaml_config)

# set up pathing for self configuration
def configSetup():
    print("[bold yellow]**please ensure you've installed the [bold green]'air for steam'[/bold green] skin before using this script!**[/bold yellow]")

    # create config directory & config file from defaults
    try:
        os.mkdir(yaml_defaults['config_path'], 0o777)
    except:
        print("[red]could not make config directory at[/red] [bold]" + yaml_defaults['config_path'] )
        pass
    try:
        with open(yaml_defaults['config_path'] + yaml_defaults['config_file'], 'w') as config:
            yaml.dump(yaml_defaults, config)
    except:
        print("[red]could not write config file...")

    yaml_config = yaml_defaults
    print("[green]successfully created config!")

# set up pathing for file locations
def userSetup(yaml_config):
    steam_skins_path = yaml_config['steam_skins_path']
    wal_cache_path = yaml_config['wal_cache_path']
    wal_template_path = yaml_config['wal_template_path']

    try:
        user = os.getlogin()
    except:
        print("[red]could not grab username...")
        pass

    print("[yellow]hello [/yellow]" + user + "[yellow]![/yellow]")


    print("[blue]is your [bold]steam skin directory[/bold] located at [/blue]'" + steam_skins_path + "'[blue]? \[y/n] ")
    ss_correct_path = pyp.inputYesNo()
    print("[blue]is your [bold]pywal cache[/bold] located at[/blue] '" + wal_cache_path + "'[blue]? \[y/n] ")
    cache_correct_path = pyp.inputYesNo()
    print("[blue]is your [bold]pywal template directory[/bold] located at [/blue]'" + wal_template_path + "'[blue]? \[y/n] ")
    template_correct_path = pyp.inputYesNo()

    if ss_correct_path == "yes" and cache_correct_path == "yes" and template_correct_path == "yes":
        print("[green]default values accepted!")
        return

    while ss_correct_path == "no":
        print("[magenta]enter correct path for steam skins directory: ")
        steam_skins_path = pyp.inputStr()
        if not os.path.exists(steam_skins_path):
            print("[red]entered path does not exist or is not accessible, try again.")
            continue
        else:
            print("[green]skin path exists!")
            yaml_config["steam_skins_path"] = steam_skins_path
            break

    while cache_correct_path == "no":
        print("[magenta]enter correct path for pywal cache directory: ")
        wal_cache_path = pyp.inputStr()
        if not os.path.exists(wal_cache_path):
            print("[red]entered path does not exist or is not accessible, try again.")
            continue
        else:
            print("[green]cache path exists!")
            yaml_config["wal_cache_path"] = wal_cache_path
            break
    
    while template_correct_path == "no":
        print("[magenta]enter correct path for pywal template directory: ")
        wal_template_path = pyp.inputStr()
        if not os.path.exists(wal_template_path):
            print("[red]entered path does not exist or is not accessible, try again.")
            continue
        else:
            print("[green]template path exists!")
            yaml_config["wal_template_path"] = wal_template_path
            break

    while True:
        print("[blue]the directories you've given are:[green]\n" + steam_skins_path + "\n" + wal_cache_path + "\n" + wal_template_path)
        print("[magenta]would you like to write these choices to file? \[y/n]")
        confirm_decision = pyp.inputYesNo()
        if confirm_decision == "yes":
            with open(yaml_config['config_path'] + yaml_config['config_file'], 'w') as config:
                yaml.dump(yaml_config, config)
            print("[green]config file updated!")
            break
        else:
            print("[red]changes cancelled.\n \n")
            userSetup()


# move template to correct location
def templateCopy(yaml_config):
    try:
        shutil.copy(yaml_config['wal_template_file'], yaml_config['wal_template_path'] + yaml_config['wal_template_file'])
    except PermissionError:
        print("[red]you don't have sufficient permissions to move the template into your [bold]pywal template directory[/bold].")
    except FileNotFoundError:
        print("[red]can't find either [bold]pywal template directory[/bold] at given path or the [bold]template file[/bold] in this directory.")

    print(yaml_config['wal_template_file'] + "[green] was moved successfully!")
    print("[magenta]refreshing pywal...")
    try:
        os.system('wal -R')
    except:
        print("[red]couldn't execute command from script. please run [/red][bold yellow]'wal -R'[/bold yellow][red] to continue.[/red]")
    print("[magenta]waiting for pywal to generate template output...\nthis only happens during configuration...")
    time.sleep(3)

# compensate for pywals lacking template system
def commaFix(yaml_config):
    src_output = yaml_config['wal_cache_path'] + yaml_config['wal_template_file']

    try: 
        with open(src_output,"r+") as f:    
            lines = f.readlines()
            lines = [line.replace(',',' ') for line in lines]
            f.seek(0)
            f.truncate()
            f.writelines(lines)
    except PermissionError:
        print("[red]you don't have sufficient permissions to access [bold]'" + yaml_config['wal_template_file'] + "'[/bold].")
    except FileNotFoundError:
        print("[red][bold]'" + yaml_config['wal_template_file'] + "'[/bold] doesn't exist.\ncheck paths and run [/red][bold yellow]'wal -R'.[/bold yellow]")

    print("[green]successfully formatted the template output!")

# if necessary, make a symlink for _pywal.styles
def stylesSymlink(yaml_config):
    src_output = yaml_config['wal_cache_path'] + yaml_config['wal_template_file']
    dst_output = yaml_config['steam_skins_path'] + yaml_config['air_path'] + yaml_config['wal_template_file']

    try:
        os.symlink(src_output, dst_output)
    except FileNotFoundError:
        print("[red]either pywal hasn't successfully created an output from template\nor your steam skin pathing is incorrect![/red]")
        print("[bold red]is " + dst_output + " a viable destination?[/bold red]" )
        quit()

    print("[green]symlink was successfully created!")

def airConfig(yaml_config):
    write_path = yaml_config['steam_skins_path'] + 'air-for-steam/config.ini'

    with open(write_path, "r") as config:
        data = config.readlines()
    
    a = 0
    b = 0

    for i in data:
        a += 1
        if "include" in i and "//include" not in i and yaml_config['wal_template_file'] not in i:
            data.remove(i)
            b += 1
            if b ==2:
                print(a, b)
                data.insert(a-3, ('    include "resource/themes/' + yaml_config['wal_template_file'] + '"'))

    with open(write_path,'w') as config:
        config.writelines(data)
    
    if b > 0:
        print("[green]updated " + write_path)

main()
