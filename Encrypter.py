import sqlite3
import CLI
import getpass
from Converters import twod_list_maker
from  randomgen import randomgenerator
from Converters import database_to_dict
from Converters import database_to_string
from Converters import letter_remover
from Scrambler import scrambler
from Scrambler import new_encryption_key_unscrambler
from Scrambler import user_panic
from Scrambler import pre_scrambler
from argon2 import PasswordHasher
CLI.logos()

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

while True:
    input_username = CLI.prompt_username()


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
        input_password_1 = CLI.prompt_password("sudo")
        if password_verification(input_password_1, users[input_username]):
            CLI.welcome(input_username)
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
            if len(cheker) == 0 :
                if CLI.prompt_confirm("Would you like to enter your Decryption key?"):
                    user_encryption_key = CLI.prompt_text("key")
                    def login_user_scrambler_key():
                        cursor1.execute("UPDATE users SET scrambler = ? WHERE username = ? " , (True, input_username))
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
                    def login_user_encyption_key():
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
                    if user_encryption_key[-1] == "S":
                        encrypt1 = login_user_scrambler_key()
                    elif user_encryption_key[-1] != "S":    
                        encrypt1 = login_user_encyption_key()
                else:
                    def login_random_key_generation():
                        cursor1.execute("UPDATE users SET scrambler = ? WHERE username = ? " , (False, input_username))
                        connection1.commit()
                        if CLI.prompt_confirm("Would you like to generate a random Encryption key?"):
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
                            return encrypt1          
                    encrypt1 = login_random_key_generation()
            else:
                cursor.execute(f'SELECT * FROM "{input_username}"')
                encrypt_demo = cursor.fetchall()
                encrypt1 = database_to_dict.database_to_dict(encrypt_demo)           
                Decrypter  = {value: key for key, value in encrypt1.items()}
            while True:
                user_input = CLI.prompt_repl(input_username)
                user_covert_input = list(user_input)
                return_list = []
                if user_input == "exit":
                    break
                if user_input.lower() == "/config":
                    user_request= CLI.EnDek_config_logo()
                    if user_request == "1":
                        user_request_1 = CLI.EnDek_encyption_settings_menu()
                        if user_request_1 == "1":
                            pre_user_encryption_key = CLI.prompt_text("key")
                            user_encryption_key = letter_remover.LetterFunctions.letter_adder(pre_user_encryption_key)
                            if len(user_encryption_key) != 0:
                                if user_encryption_key[-1] == "S":
                                    cursor1.execute("UPDATE users SET scrambler = ? WHERE username = ? " , (True, input_username))
                                    unscrambler_key = CLI.prompt_text("Scrambler Key")
                                    user_encryption_key_unscrambled = new_encryption_key_unscrambler(scrambeled_encryption_key = user_encryption_key, unscrambler = unscrambler_key , username = input_username)
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
                                    CLI.show_key("Scrambler Key", scrambled_encyption_key_output[1])
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
                                    cursor.execute(f'SELECT * FROM "{input_username}"')
                                    scrambler_encryption_key = cursor.fetchall()
                                    scrambler_encryption_key_2 = letter_remover.LetterFunctions.letter_remover(database_to_string.database_to_string(scrambler_encryption_key))
                                    scrambled_encyption_key_output = scrambler(scrambler_encryption_key_2, input_username)
                                    CLI.show_result(scrambled_encyption_key_output[0])
                                    CLI.show_key("Scrambler Key", scrambled_encyption_key_output[1])
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
                                        CLI.show_key("Encryption key", final_returned_string[0])
                                        CLI.show_key("Scrambler key", final_returned_string[1])
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
                            connection.commit()
                            CLI.success("DataBase is clear")
                            cursor.execute(f'SELECT * FROM "{input_username}"') 
                            encrypt_demo = cursor.fetchall()
                            user_panic(input_username)
                            encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                            Decrypter  = {value: key for key, value in encrypt1.items()}
                    elif user_request == "2":
                        user_request_2 = CLI.Account_settings_menu()
                        if user_request_2 == "2":
                            conformation = CLI.Account_confirmation_menu()
                            if conformation == "1":
                                cursor1.execute(f'DELETE FROM users WHERE username = (?)', (input_username,))
                                connection1.commit()
                                cursor.execute(f'DELETE FROM "{input_username}"')
                                connection.commit()
                                cursor.execute(f'SELECT * FROM "{input_username}"') 
                                encrypt_demo = cursor.fetchall()
                                user_panic(input_username)
                                encrypt1 = database_to_dict.database_to_dict(encrypt_demo)
                                Decrypter  = {value: key for key, value in encrypt1.items()}
                                CLI.success("Account deleted successfully...")
                        elif user_request_2 == "1":
                            break
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
                                return_list.append(encrypt1[i])               
                                if len(user_covert_input) == len(return_list):
                                    return_list.append("E")
                                    return_sentence = "". join(return_list)
                                    CLI.show_result(return_sentence)
                            except KeyError:
                                CLI.error("invalid characters")
        elif input_password_1 != users.get(input_username):
            CLI.error("wrong password!!")
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
                if key_before[-1] == "S":
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
                            if user_input == "exit":
                                break
                            for i in user_covert_input:
                                try:
                                    return_list.append(encrypt1[i])               
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
                        if user_input == "exit":
                            break
                        for i in user_covert_input:
                            try:
                                return_list.append(dict_1[i])               
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
