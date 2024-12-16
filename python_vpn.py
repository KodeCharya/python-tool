import os
import subprocess

class VPNManager:
    def __init__(self):
        self.servers = []
        self.current_server = None
        self.vpn_status = False

    def add_server(self, server_config_path):
        if os.path.exists(server_config_path):
            self.servers.append(server_config_path)
            print(f"Server added: {server_config_path}")
        else:
            print("Error: Server configuration file not found.")

    def list_servers(self):
        if not self.servers:
            print("No servers available.")
            return

        print("Available servers:")
        for idx, server in enumerate(self.servers):
            print(f"{idx + 1}. {server}")

    def switch_server(self, server_index):
        if server_index < 1 or server_index > len(self.servers):
            print("Invalid server index.")
            return

        if self.vpn_status:
            self.vpn_off()

        self.current_server = self.servers[server_index - 1]
        print(f"Switched to server: {self.current_server}")

    def vpn_on(self):
        if self.current_server is None:
            print("No server selected. Please select a server first.")
            return

        try:
            # Assuming OpenVPN for demonstration purposes
            self.vpn_process = subprocess.Popen([
                "openvpn",
                "--config",
                self.current_server
            ])
            self.vpn_status = True
            print("VPN is now ON.")
        except FileNotFoundError:
            print("Error: OpenVPN is not installed or not in the PATH.")
        except Exception as e:
            print(f"Error starting VPN: {e}")

    def vpn_off(self):
        if not self.vpn_status:
            print("VPN is already OFF.")
            return

        if self.vpn_process:
            self.vpn_process.terminate()
            self.vpn_process.wait()
        self.vpn_status = False
        print("VPN is now OFF.")

    def main_menu(self):
        while True:
            print("\nVPN Manager")
            print("1. Add new server")
            print("2. List servers")
            print("3. Switch server")
            print("4. Turn VPN ON")
            print("5. Turn VPN OFF")
            print("6. Exit")

            choice = input("Enter your choice: ")
            if choice == "1":
                server_path = input("Enter the path to the server configuration file: ")
                self.add_server(server_path)
            elif choice == "2":
                self.list_servers()
            elif choice == "3":
                self.list_servers()
                server_index = int(input("Enter the server number to switch to: "))
                self.switch_server(server_index)
            elif choice == "4":
                self.vpn_on()
            elif choice == "5":
                self.vpn_off()
            elif choice == "6":
                if self.vpn_status:
                    self.vpn_off()
                print("Exiting VPN Manager.")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    vpn_manager = VPNManager()
    vpn_manager.main_menu()
