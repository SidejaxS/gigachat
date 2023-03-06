import tkinter as tk
from tkinter import messagebox
import socket
import threading

window = tk.Tk()
window.title("Cliente")
username = " "
ServerIP = " "

# network client
client = None
HOST_PORT = 8080
HOST_ADDR = " "

#Entrada que se encarga de la inserción del nombre de usuario
topFrame = tk.Frame(window)
lblName = tk.Label(topFrame, text = "Nombre:").pack(side=tk.LEFT)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)

#Entrada que se encarga de recibir la ip del servidor al  que te quieres conectar
lblIP = tk.Label(topFrame, text="Server IP:")
lblIP.pack(side=tk.LEFT)
entIP = tk.Entry(topFrame)
entIP.pack(side=tk.LEFT)

#Botón que se encarga de conectar al cliente con el servidor
btnConnect = tk.Button(topFrame, text="Connect", command=lambda : connect())
btnConnect.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP)

#Esto se encarga principalmente de la parte visual del texto y de la scrollbar del chat
displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text="Bienvenido a la sala del chat de python!").pack()
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)

#Esto se encarga de la parte visual de la entrada de texto
bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=2, width=55)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)


def connect():
    global username, client, HOST_ADDR
    if len(entName.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!", message="Debes insertar tu nombre y el servidor primero!")
    else:
        username = entName.get()
        print(entIP.get())
        HOST_ADDR = entIP.get()
        connect_to_server(username)

def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) # Envia el nombre al servidor tras conectarse, que se utilizara para la lista de clientes

        entName.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        #Este hilo se encarga de mantener la conexión con el servidor y el intercambio de mensajes
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="No se puede conectar al servidor " + HOST_ADDR + " en el puerto " + str(HOST_PORT) + " Puede que el servidor no este disponible o que hayas insertado mal su IP.")


def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server: break
        
        #FROM SERVER ES EL MENSAJE ACTUAL QUE RECIBES DEL SERVIDOR!!!           POSIBLE USO DE ENCRPTACION

        # display message from server on the chat window

        # enable the display area and insert the text and then disable.
        # why? Apparently, tkinter does not allow us insert into a disabled Text widget :(
        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)
        print(texts)
        if len(texts) < 1:
            tkDisplay.insert(tk.END, from_server)
        else:
            tkDisplay.insert(tk.END, "\n\n"+ from_server)

        tkDisplay.config(state=tk.DISABLED)
        tkDisplay.see(tk.END)

        # print("Server says: " +from_server)

    sck.close()
    window.destroy()


def getChatMessage(msg):

    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()

    # enable the display area and insert the text and then disable.
    # why? Apparently, tkinter does not allow use insert into a disabled Text widget :(
    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message") # no line
    else:
        tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    send_mssage_to_server(msg)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END)


def send_mssage_to_server(msg):
    client_msg = str(msg)

    if msg == "exit":
        client.close()
        window.destroy()
    elif "/msg" in msg:
        print("Sending private message")
        client.send(client_msg.encode())
    else:
        print("Sending message")
        client.send(client_msg.encode())
        

window.mainloop()
