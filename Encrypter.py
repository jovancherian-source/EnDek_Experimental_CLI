import sqlite3
import CLI
import getpass
from Converters import twod_list_maker
from randomgen import randomgenerator
from Converters import database_to_dict
from Converters import database_to_string
from Converters import letter_remover
from Scrambler import scrambler
from Scrambler import new_encryption_key_unscrambler
from Scrambler import user_panic
from Scrambler import pre_scrambler
from Scrambler import scrambeler_updater
from argon2 import PasswordHasher
import string
from Functionalities import updater


CLI.logos()

EnDek_verison = "2.7.0"
Experimental_CLI_Version = "1.5.0"
EnDek_name = "Ludicrous"
latest_version = updater.intial_update_checker(EnDek_verison)
if latest_version is not None:
    CLI.info(latest_version)

class AccoutDeletion(Exception):
    pass

def password_hashing(password):
    ph = PasswordHasher()
    return ph.hash(str(password))

def password_verification(password, hashed_password):
    ph = PasswordHasher()
    try:
        ph.verify(hashed_password, str(password))
        return True
    except Exception:
        return False

def main():
    while True:
        try:
            input_username = CLI.prompt_username()
        except KeyboardInterrupt:
            CLI.success("Thank You for using EnDek")
            return
        if input_username == "/exit":
            return
        if not all(char in string.ascii_letters for char in input_username):
            CLI.error("please only plain English letters are accepted for usernames! Spaces are NOT allowed.")
            continue

        connection1 = sqlite3.connect("users.db")
        cursor1 = connection1.cursor()
        cursor1.execute("""
        CREATE TABLE IF NOT EXISTS users(
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    scrambler BOOLEAN)
        """)
        cursor1.execute("SELECT * FROM users ")
        users = database_to_dict.database_to_dict(cursor1.fetchall())


        if input_username in users:
            try:
                input_password_1 = CLI.prompt_password("sudo")
                if password_verification(input_password_1, users[input_username]):
                    CLI.welcome(input_username)
                    input_password_1 = ""
                    
                    connection = sqlite3.connect("encyption_keys.db")
                    cursor = connection.cursor()
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS "{input_username}"(
                                encryption_key TEXT PRIMARY KEY,
                                encryption_value TEXT)
                    """)
                    connection.commit()
                    cursor.execute(f'SELECT * FROM "{input_username}"') 
                    cheker = cursor.fetchall()
                    try:
                        trial_times = 0
                        accept_checker = False
                        while len(cheker) == 0 and trial_times < 5 and accept_checker != True:
                            trial_times += 1
                            if CLI.prompt_confirm("Would you like to enter your Decryption key?"):
                                user_encryption_key = CLI.prompt_text("key")
                                def login_user_scrambler_key(user_encryption_key):
                                    cursor1.execute("UPDATE users SET scrambler = ? WHERE username = ? " , (True, input_username))
                                    connection1.commit()
                                    unscrambler_key = CLI.prompt_text("Scrambler Key")
                                    user_encryption_key_unscrambled = new_encryption_key_unscrambler(scrambeled_encryption_key = user_encryption_key, unscrambler = unscrambler_key , username = input_username)
                                    user_encryption_key_unscrambled = letter_remover.LetterFunctions.letter_adder(user_encryption_key_unscrambled)
                                    cursor.execute(f'DELETE FROM "{input_username}"')
                                    updated_encryption_key = twod_list_maker.list_maker(user_encryption_key_unscrambled)
                                    for key in updated_encryption_key:
                                        cursor.execute(f'INSERT INTO "{input_username}"( encryption_key , encryption_value) VALUES(?,?)', (key[0] , key[1]))
                                    CLI.success("Encryption key added successfully...")
                                    cursor.execute(f'SELECT * FROM "{input_username}"')
                                    encrypt_demo = cursor.fetchall()
                                    encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                                    connection.commit()
                                    return encrypt1
                                def login_user_encyption_key(user_encryption_key):
                                    cursor1.execute("UPDATE users SET scrambler = ? WHERE username = ? " , (False, input_username))
                                    connection1.commit()
                                    user_encryption_key_added = letter_remover.LetterFunctions.letter_adder(user_encryption_key)
                                    cursor.execute(f'DELETE FROM "{input_username}"')
                                    updated_encryption_key = twod_list_maker.list_maker(user_encryption_key_added)
                                    for key in updated_encryption_key:
                                        cursor.execute(f'INSERT INTO "{input_username}"( encryption_key , encryption_value) VALUES(?,?)', (key[0] , key[1]))
                                    CLI.success("Encryption key added successfully...")
                                    cursor.execute(f'SELECT * FROM "{input_username}"')
                                    encrypt_demo = cursor.fetchall()
                                    encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                                    connection.commit()
                                    connection1.commit()
                                    return encrypt1
                                if user_encryption_key == "":
                                    CLI.error("Encryption key cannot be empty...")
                                    accept_checker = False
                                elif user_encryption_key != "":
                                    if user_encryption_key[-1] == "S":
                                        accept_checker = True
                                        encrypt1 = login_user_scrambler_key(user_encryption_key)
                                    elif user_encryption_key[-1] != "S":    
                                        accept_checker = True
                                        encrypt1 = login_user_encyption_key(user_encryption_key)
                            else:
                                def login_random_key_generation():
                                    cursor1.execute("UPDATE users SET scrambler = ? WHERE username = ? " , (False, input_username))
                                    connection1.commit()
                                    if CLI.prompt_confirm("Would you like to generate a random Encryption key?"):
                                        accept_checker = True
                                        random_generated_string = randomgenerator()
                                        random_generated_list = twod_list_maker.list_maker(random_generated_string)
                                        for key_letter in random_generated_list:
                                            cursor.execute(f'INSERT INTO "{input_username}"(encryption_key, encryption_value) VALUES(?,?)', (key_letter[0], key_letter[1]))
                                        CLI.show_result(letter_remover.LetterFunctions.letter_remover(random_generated_string))
                                        cursor.execute(f'SELECT * FROM "{input_username}"')
                                        encrypt_demo = cursor.fetchall()
                                        encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                                        connection.commit()
                                        CLI.success("Encryption key was generated and was added as a key...")
                                        return encrypt1, accept_checker
                                    else:
                                        accept_checker = False
                                        return False, accept_checker          
                                loger_checker = login_random_key_generation()
                                if loger_checker[1] != False:
                                    encrypt1 = loger_checker[0]
                                    accept_checker = True
                                elif loger_checker[1] == False:
                                    accept_checker = False
                        if trial_times > 4:
                            CLI.error("you have no enrcyption key!! add one via config menu...")
                        else:
                            cursor.execute(f'SELECT * FROM "{input_username}"')
                            db_global_user_encryption_key = cursor.fetchall()
                            global_user_encryption_key = letter_remover.LetterFunctions.letter_remover(database_to_string.database_to_string(db_global_user_encryption_key))
                            encrypt1 = database_to_dict.database_to_dict(db_global_user_encryption_key)           
                            Decrypter  = {value: key for key, value in encrypt1.items()}
                        while True:
                            user_input = CLI.prompt_repl(input_username)
                            user_covert_input = list(user_input)
                            return_list = []
                            if user_input == "/exit":
                                return
                            if user_input == "/logout":
                                break
                            if user_input.lower() == "/config":
                                user_request = CLI.EnDek_config_logo()
                                if user_request == "1":
                                    user_request_1 = CLI.EnDek_encyption_settings_menu()
                                    if user_request_1 == "1":
                                        pre_user_encryption_key = CLI.prompt_text("key")
                                        user_encryption_key = list(pre_user_encryption_key)
                                        if len(user_encryption_key) != 0:
                                            if user_encryption_key[-1] == "S":
                                                cursor1.execute("UPDATE users SET scrambler = ? WHERE username = ? " , (True, input_username))
                                                unscrambler_key = CLI.prompt_text("Scrambler Key")
                                                user_encryption_key_unscrambled = new_encryption_key_unscrambler(scrambeled_encryption_key = pre_user_encryption_key, unscrambler = unscrambler_key , username = input_username)
                                                user_encryption_key_unscrambled = letter_remover.LetterFunctions.letter_adder(user_encryption_key_unscrambled)
                                                cursor.execute(f'DELETE FROM "{input_username}"')
                                                updated_encryption_key = twod_list_maker.list_maker(user_encryption_key_unscrambled)
                                                for key in updated_encryption_key:
                                                    cursor.execute(f'INSERT INTO "{input_username}"( encryption_key , encryption_value) VALUES(?,?)', (key[0] , key[1]))
                                                CLI.success("Encryption key updated successfully...")
                                                cursor.execute(f'SELECT * FROM "{input_username}"')
                                                encrypt_demo = cursor.fetchall()
                                                encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                                                Decrypter  = {value: key for key, value in encrypt1.items()}
                                                connection.commit()
                                                connection1.commit()
                                            elif user_encryption_key[-1] != "S":
                                                cursor.execute(f'DELETE FROM "{input_username}"')
                                                updated_encryption_key = twod_list_maker.list_maker(user_encryption_key)
                                                for key in updated_encryption_key:
                                                    cursor.execute(f'INSERT INTO "{input_username}"( encryption_key , encryption_value) VALUES(?,?)', (key[0] , key[1]))
                                                CLI.success("Encryption key updated successfully...")
                                                cursor.execute(f'SELECT * FROM "{input_username}"')
                                                encrypt_demo = cursor.fetchall()
                                                encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                                                Decrypter  = {value: key for key, value in encrypt1.items()}
                                                connection.commit()
                                        elif len(user_encryption_key) == 0:
                                            CLI.error("Encryption key cannot be empty...")
                                    elif user_request_1 == "2":
                                        if CLI.prompt_confirm("Would you like to generate a random Encryption key?"):
                                            is_using_srambler  = cursor1.execute(f'SELECT scrambler FROM users WHERE username = ?' , (input_username,)).fetchone()[0]
                                            if is_using_srambler == 1:
                                                cursor.execute(f'DELETE FROM "{input_username}"')
                                                random_generated_string = randomgenerator()
                                                random_generated_list = twod_list_maker.list_maker(random_generated_string)
                                                for key_letter in random_generated_list:
                                                    cursor.execute(f'INSERT INTO "{input_username}"(encryption_key, encryption_value) VALUES(?,?)', (key_letter[0], key_letter[1]))
                                                random_generated_string_full = letter_remover.LetterFunctions.letter_remover(random_generated_string)
                                                scrambled_encyption_key_output = pre_scrambler(random_generated_string_full, input_username)
                                                CLI.show_result(scrambled_encyption_key_output[0])
                                                CLI.show_result(scrambled_encyption_key_output[1])
                                                cursor.execute(f'SELECT * FROM "{input_username}"')
                                                encrypt_demo = cursor.fetchall()
                                                encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                                                Decrypter  = {value: key for key, value in encrypt1.items()}
                                                connection.commit()
                                                CLI.success("Encryption key was generated and was added as a key...")
                                            elif is_using_srambler == 0:
                                                random_generated_string = randomgenerator()
                                                random_generated_list = twod_list_maker.list_maker(random_generated_string)
                                                cursor.execute(f'DELETE FROM "{input_username}"')
                                                for key_letter in random_generated_list:
                                                    cursor.execute(f'INSERT INTO "{input_username}"(encryption_key, encryption_value) VALUES(?,?)', (key_letter[0], key_letter[1]))
                                                random_generated_string_full = letter_remover.LetterFunctions.letter_remover(random_generated_string)
                                                CLI.show_result(random_generated_string_full)
                                                cursor.execute(f'SELECT * FROM "{input_username}"')
                                                encrypt_demo = cursor.fetchall()
                                                encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                                                Decrypter  = {value: key for key, value in encrypt1.items()}
                                                connection.commit()
                                                CLI.success("Encryption key was generated and was added as a key...")
                                    elif user_request_1 == "3":
                                        cursor1.execute("SELECT scrambler FROM users WHERE username = ? " , (input_username,))
                                        scrambler_status = cursor1.fetchone()[0]
                                        if scrambler_status == 1:
                                            user_request_for_pre_scrambler = CLI.Scramble_settings_menu()
                                            if user_request_for_pre_scrambler == "1":
                                                scrambler_changer_user_request = CLI.new_Scramble_settings_menu()
                                                if scrambler_changer_user_request == "1":
                                                    scrambler_key_new = CLI.new_Scramble_key_for_pre_user()
                                                    if len(scrambler_key_new) == 0:
                                                        CLI.error("Encryption key cannot be empty...")
                                                    else:
                                                        new_encryption_scrambler = scrambeler_updater(scrambler_key= scrambler_key_new, username = input_username)
                                                        CLI.success("Scrambler key updated successfully...")
                                                elif scrambler_changer_user_request == "2":
                                                    new_encryption_scrambler = scrambler(Encryption_key = global_user_encryption_key, username = input_username)
                                                    CLI.success("Encryption key updated successfully...")
                                                    CLI.show_key("New Scrambler key", str(new_encryption_scrambler[1]))
                                            elif user_request_for_pre_scrambler == "2":
                                                cursor1.execute("UPDATE users SET scrambler = ? WHERE username = ? " , (False, input_username))
                                                connection1.commit()
                                        elif scrambler_status == 0 or scrambler_status is None:
                                            user_request_scrambler = CLI.first_Scramble_settings_menu()
                                            if user_request_scrambler == "1":
                                                cursor1.execute("UPDATE users SET scrambler = ? WHERE username = ? " , (True, input_username))
                                                connection1.commit()
                                                cursor.execute(f'SELECT * FROM "{input_username}"')
                                                scrambler_encryption_key = cursor.fetchall()
                                                scrambler_encryption_key_2 = letter_remover.LetterFunctions.letter_remover(database_to_string.database_to_string(scrambler_encryption_key))
                                                scrambled_encyption_key_output = scrambler(scrambler_encryption_key_2, input_username)
                                                CLI.show_result(scrambled_encyption_key_output[0])
                                                CLI.show_key("Scrambler Key", scrambled_encyption_key_output[1])
                                    elif user_request_1 == "4":
                                        user_database_security = CLI.prompt_password("sudo")
                                        if password_verification(user_database_security, users[input_username]):
                                            cursor.execute(f'SELECT * FROM "{input_username}"')
                                            encrypt_demo = cursor.fetchall() 
                                            if len(encrypt_demo) == 0:
                                                CLI.error("No encryption key found...")
                                            elif len(encrypt_demo) != 0:
                                                is_using_srambler  = cursor1.execute(f'SELECT scrambler FROM users WHERE username = ?' , (input_username,)).fetchone()[0]
                                                if is_using_srambler == 1:
                                                    pre_returned_string = database_to_string.database_to_string(encrypt_demo)
                                                    returned_string = letter_remover.LetterFunctions.letter_remover(pre_returned_string)
                                                    final_returned_string = pre_scrambler(returned_string, input_username)
                                                    CLI.show_key("Encryption key", str(final_returned_string[0]))
                                                    CLI.show_key("Scrambler key", str(final_returned_string[1]))
                                                    CLI.success("Encryption key and Scrambler key exported successfully...")
                                                elif is_using_srambler == 0:
                                                    pre_returned_string = database_to_string.database_to_string(encrypt_demo)
                                                    returned_string = letter_remover.LetterFunctions.letter_remover(pre_returned_string)
                                                    CLI.show_key("Encryption key", returned_string)
                                                    CLI.success("Encryption key exported successfully...")
                                elif user_request == "3":
                                    user_request_3 = CLI.Database_settings_menu()
                                    if user_request_3 == "1":
                                        cursor.execute(f'DELETE FROM "{input_username}"')
                                        cursor.execute(f'DROP TABLE "{input_username}"')
                                        connection.commit()
                                        connection.close()
                                        user_panic(input_username)
                                        connection1.close()
                                        CLI.success("DataBase is clear")
                                        if __name__ == "__main__":
                                            main()
                                        return
                                elif user_request == "2":
                                    user_request_2 = CLI.Account_settings_menu()
                                    if user_request_2 == "2":
                                        conformation = CLI.Account_confirmation_menu()
                                        if conformation == "1":
                                            cursor.execute(f'DELETE FROM "{input_username}"')
                                            connection.commit()
                                            is_using_srambler  = cursor1.execute(f'SELECT scrambler FROM users WHERE username = ?' , (input_username,)).fetchone()[0]
                                            if is_using_srambler == 1:
                                                user_panic(input_username)
                                            cursor1.execute(f'DELETE FROM users WHERE username = (?)', (input_username,))
                                            connection1.commit()
                                            cursor.execute(f'SELECT * FROM "{input_username}"') 
                                            cursor1.execute("SELECT * FROM users ")
                                            users = database_to_dict.database_to_dict(cursor1.fetchall())
                                            encrypt_demo = cursor.fetchall()
                                            encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                                            Decrypter  = {value: key for key, value in encrypt1.items()}
                                            raise AccoutDeletion()
                                    elif user_request_2 == "1":
                                        break
                                elif user_request == "4":
                                    user_request_dual_endek = CLI.endek_dual_settings()
                                    if user_request_dual_endek == "1":
                                        CLI.logos()
                                        cursor1.execute("SELECT * FROM users ")
                                        users_number = len(cursor1.fetchall())
                                        is_using_srambler = cursor1.execute(f'SELECT scrambler FROM users WHERE username = ?', (input_username,)).fetchone()[0]
                                        CLI.show_about(
                                            version=EnDek_verison,
                                            cli_version=Experimental_CLI_Version,
                                            key_status="Active",
                                            users_count=users_number,
                                            scrambler_enabled=(is_using_srambler == 1)
                                        )
                                    elif user_request_dual_endek == "2":
                                        update_info = updater.update_checker(EnDek_verison)
                                        if update_info:
                                            CLI.info(update_info)
                            if len(user_covert_input) !=0 :
                                if user_covert_input[-1] == "E" and user_input !="/config":
                                    cursor.execute(f'SELECT * FROM "{input_username}"')
                                    encrypt_demo = cursor.fetchall()
                                    encrypt = database_to_dict.database_to_dict(encrypt_demo)
                                    Decrypter  = {value: key for key, value in encrypt1.items()}
                                    for i in user_covert_input:
                                        if i in Decrypter:
                                            return_list.append(Decrypter.get(i , "letter not found :("))
                                    return_word = "". join(return_list)
                                    CLI.show_result(return_word)
                                if user_covert_input[-1] != "E" and user_input !="/config":
                                    for i in user_covert_input :
                                        try:
                                            return_list.append(encrypt1[i.lower()])               
                                            if len(user_covert_input) == len(return_list):
                                                return_list.append("E")
                                                return_sentence = "". join(return_list)
                                                CLI.show_result(return_sentence)
                                        except KeyError:
                                            CLI.error("invalid character: " + i)
                        connection.close()
                        connection1.close()
                    except AccoutDeletion:
                        CLI.success("account deleted sucessfully...")
                    except KeyboardInterrupt:
                        CLI.success("Thank You for using EnDek")
                        return
                    except Exception as e:
                        CLI.error(f"error occured: {e}")
                        CLI.error("if you were trying to enter any kind of input, please make sure it is a valid Type of input in EnDek")
                elif password_verification(input_password_1, users[input_username]) == False:
                    CLI.error("wrong password!!")
            except KeyboardInterrupt:
                CLI.success("Thank You for using EnDek")
                return
            except Exception as e:
                CLI.error(f"An error occurred while fetching encryption keys: {e}")
        elif input_username not in users:
            if CLI.prompt_confirm("User not found. Would you like to create a new user?"):
                new_user_password = password_hashing(CLI.prompt_password("password"))
                recheck = CLI.prompt_password("Re-enter password")
                if password_verification(recheck, new_user_password):
                    cursor1.execute("INSERT INTO users(username, password, scrambler) VALUES(?, ?, ?)", (input_username, new_user_password, False))
                    connection1.commit()
                    CLI.welcome_new_user(input_username)
                else:
                    CLI.error("passwords do not match!!")

            else:
                if CLI.prompt_confirm("Do you have an encryption key?"):
                    key_before = CLI.prompt_text("Key")
                    if len(key_before) == 0:
                        CLI.error("Encryption key cannot be empty...")
                    elif key_before[-1] == "S":
                        CLI.error("you cannot decrypt without signing in.")
                    elif key_before[-1] != "S":
                        key = letter_remover.LetterFunctions.letter_adder(key_before)
                        unknown_user_two_d  = twod_list_maker.list_maker(key)
                        encrypt1 = database_to_dict.database_to_dict(unknown_user_two_d)        
                        x = 0
                        while  x < 5:
                                x += 1
                                user_input = CLI.prompt_guest_repl()
                                user_covert_input = list(user_input)
                                return_list = []
                                if user_input == "exit" or user_input == "/exit":
                                    break
                                for i in user_covert_input:
                                    try:
                                        return_list.append(encrypt1[i.lower()])               
                                        return_sentence = "" . join(return_list)
                                        if len(user_covert_input) == len(list(return_sentence)):
                                            return_list.append("E")
                                            return_sentence = "".join(return_list)                         
                                            CLI.show_result(return_sentence)
                                    except KeyError:
                                        if user_covert_input[-1] == "E":
                                            CLI.error("you cannot decrypt without a username")
                                        else:
                                            CLI.error("invalid characters")
                else:
                    if CLI.prompt_confirm("Would you like to generate Encryption key?"):
                        key = randomgenerator()
                        two_dimentional = twod_list_maker.list_maker(key)
                        dict_1 = database_to_dict.database_to_dict(two_dimentional)
                        key_after = letter_remover.LetterFunctions.letter_remover(key)
                        CLI.show_result(key_after)
                        CLI.success("command successful...")
                        x =0 
                        while x <6:
                            x += 1
                            user_input = CLI.prompt_guest_repl()
                            user_covert_input = list(user_input)
                            return_list = []
                            if user_input == "exit" or user_input == "/exit":
                                break
                            for i in user_covert_input:
                                try:
                                    return_list.append(dict_1[i.lower()])               
                                    return_sentence = "" . join(return_list)
                                    if len(user_covert_input) == len(list(return_sentence)):
                                        return_list.append("E")
                                        return_sentence = "".join(return_list) 
                                        CLI.show_result(return_sentence)
                                except KeyError:
                                    if user_covert_input[-1] == "E":
                                        CLI.error("you cannot decrypt without a username")
                                    else:
                                        CLI.error("invalid characters")

if __name__ == "__main__":
    main()
