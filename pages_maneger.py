import tkinter as tk
from tkinter import messagebox
import json
import os


COLORS = {
    'background': '#F0F0F0',
    'surface': '#FFFFFF',
    'primary': '#1F5F8B',
    'secondary': '#8B2F5A',
    'success': '#27AE60',
    'error': '#E74C3C',
    'text_primary': '#000000',
    'text_secondary': '#555555',
    'gray': '#7F8C8D'
}
FONTS = {
    'title': ('Arial', 20, 'bold'),
    'heading': ('Arial', 14, 'bold'),
    'body': ('Arial', 12),
    'button': ('Arial', 12, 'bold')
}
WINDOW_SIZES = {'home': '900x700', 'category': '900x700'}
Purple = "#4e396e"

PRODUCTS_FILE = "products.json"



def load_products_file():
    try :
        with open(PRODUCTS_FILE, 'r') as f :
            return json.load(f)
    except :
        return {}


def save_products_file(data) :

    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def binary_search(products, target, key="name") :

    low, high = 0, len(products) - 1
    target = target.strip().lower()

    while low <= high :
        mid = (low + high) // 2
        product_value = str(products[mid][key]).lower()
        if product_value == target:
            return mid
        elif product_value < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def merge_sort(products, key="price", reverse=False):
    if len(products) <= 1:
        return products[:]
    mid = len(products) // 2
    left = merge_sort(products[:mid], key, reverse)
    right = merge_sort(products[mid:], key, reverse)
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if reverse:
            if left[i][key] > right[j][key]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        else:
            if left[i][key] < right[j][key] :
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

class Stack :
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return len(self.items) == 0

    def push(self, win):
        if self.items:
            self.items[-1].withdraw()
        self.items.append(win)
        win.deiconify()

    def pop(self) :
        if len(self.items) <= 1:
            return None
        current_win = self.items.pop()
        current_win.destroy()
        previous_win = self.items[-1]
        previous_win.deiconify()
        return previous_win


class CartManager :

    def __init__(self) :
        self.cart = []
        self.total_price = 0
        self.products = load_products_file()

    def reload_products(self) :
        self.products = load_products_file()

    def save_products(self) :
        save_products_file(self.products)

    def add_to_cart(self, product_id, category):
        if category not in self.products:
            messagebox.showinfo("❌", f"Category '{category}' not found.")
            return
        for product in self.products[category]:
            if product.get("id") == product_id:
                if product.get("stock") <= 0 :
                    messagebox.showinfo("❌", f"Sorry, {product['name']} is out of stock.")
                    return
                for item in self.cart:
                    if item["id"] == product_id and item["category"] == category:
                        if item["quantity"] >= product["stock"]:
                            messagebox.showinfo("❌", f"Cannot add more. Only {product['stock']} left in stock.")
                            return
                        item["quantity"] += 1
                        self.total_price += product["price"]
                        messagebox.showinfo("✅", f"{product['name']} quantity updated to {item['quantity']}.")
                        return

                new_item = product.copy()
                new_item["quantity"] = 1
                new_item["category"] = category
                self.cart.append(new_item)
                self.total_price += product["price"]

                messagebox.showinfo("✅", f"{product['name']} added to cart.")

                return

        messagebox.showinfo("❌", "Product not found.")

    def remove_from_cart(self, product_id, category) :

        for item in list(self.cart) :

            if item["id"] == product_id and item["category"] == category :

                item["quantity"] -= 1
                self.total_price -= item["price"]
                if item["quantity"] <= 0:
                    self.cart.remove(item)

                return

    def clear_cart(self) :
        if not self.cart :
            messagebox.showinfo("ℹ️", "Cart is already empty.")
            return
        if messagebox.askyesno("Confirm", "Clear cart?"):
            self.cart = []
            self.total_price = 0

    def checkout(self):
        if not self.cart:
            return "❗ Your cart is empty."
        if not messagebox.askyesno("Confirm", "Proceed to checkout?"):
            return "❌ Checkout cancelled."

        self.reload_products()

        insufficient = []
        for item in self.cart:
            cat = item["category"]
            for prod in self.products.get(cat, []):
                if prod.get("id") == item["id"]:
                    if prod.get("stock", 0) < item["quantity"]:
                        insufficient.append(
                            f"{prod['name']} (Available: {prod.get('stock', 0)}, In Cart: {item['quantity']})")
                    break

        if insufficient:
            return "⚠️ Not enough stock for:\n" + "\n".join(insufficient)

        for item in self.cart :
            cat = item["category"]
            for prod in self.products[cat]:
                if prod.get("id") == item["id"]:
                    prod["stock"] -= item["quantity"]
                    break

        self.save_products()
        self.cart = []
        self.total_price = 0

        return "✅ Checkout successful."

class CategoryPage(tk.Toplevel) :
    def __init__(self, parent, category_name, title, cart_manager, nav_stack) :
        super().__init__(parent)
        self.cart_manager = cart_manager
        self.nav_stack = nav_stack
        self.category_name = category_name

        self.geometry(WINDOW_SIZES['category'])
        self.title(title)
        self.configure(bg=COLORS['background'])
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        try :
            with open(PRODUCTS_FILE, "r") as f:
                all_products = json.load(f)
        except :
            all_products = {}

        self.products = all_products.get(category_name, [])

        header_frame = tk.Frame(self, bg=COLORS['background'])
        header_frame.pack(fill="x", pady=20, padx=20)

        tk.Button(header_frame, text="← Back", fg=COLORS['primary'], bg=COLORS['background'],
                  font=FONTS['body'], bd=0, command=self.go_back).pack(side="left")

        tk.Label(header_frame, text=title, font=FONTS['title'], fg=COLORS['text_primary'],
                 bg=COLORS['background']).pack(side="left", expand=True)

        search_sort_frame = tk.Frame(header_frame, bg=COLORS['background'])
        search_sort_frame.pack(side="right")

        search_input_frame = tk.Frame(search_sort_frame, bg=COLORS['background'])
        search_input_frame.pack(pady=5)

        tk.Label(search_input_frame, text="Search:", bg=COLORS['background'], font=FONTS['body']).pack(side="left",
                                                                                                       padx=5)
        self.search_var = tk.StringVar()

        tk.Entry(search_input_frame, textvariable=self.search_var, width=15).pack(side="left", padx=5)
        tk.Button(search_input_frame, text="Search", command=self.search_item, bg=COLORS['secondary'], fg="white",
                  font=FONTS['button']).pack(side="left")

        sort_button_frame = tk.Frame(search_sort_frame, bg=COLORS['background'])
        sort_button_frame.pack(pady=5)

        tk.Button(sort_button_frame, text="Sort by Price", command=lambda: self.sort_products(False),
                  bg=COLORS['secondary'], fg="white", font=FONTS['button']).pack(side="left", padx=5)

        self.products_frame = tk.Frame(self, bg=COLORS['background'])
        self.products_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.display_products(self.products)

    def display_products(self, products) :

        for widget in self.products_frame.winfo_children():
            widget.destroy()

        for idx, product in enumerate(products):
            frame = tk.Frame(self.products_frame, bg=COLORS['surface'], relief="flat", bd=1)
            frame.grid(row=idx // 3, column=idx % 3, padx=10, pady=10, sticky="nsew")

            tk.Label(frame, text=product["name"], font=FONTS['heading'], fg=COLORS['primary'],
                     bg=COLORS['surface']).pack(pady=(10, 0))
            tk.Label(frame, text=f"${product['price']}", font=FONTS['title'], fg=COLORS['secondary'],
                     bg=COLORS['surface']).pack(pady=(0, 5))
            tk.Label(frame, text=f"Brand: {product['brand']}", font=FONTS['body'], fg=COLORS['text_secondary'],
                     bg=COLORS['surface']).pack()
            tk.Label(frame, text=f"Year: {product['model year']}", font=FONTS['body'], fg=COLORS['text_secondary'],
                     bg=COLORS['surface']).pack()
            tk.Label(frame, text=f"Stock: {product['stock']}", font=FONTS['body'], fg=COLORS['text_secondary'],
                     bg=COLORS['surface']).pack(pady=(0, 10))

            tk.Button(frame, text="Add to Cart", bg=COLORS['secondary'], fg="white", font=FONTS['button'],
                      command=lambda p=product: self.cart_manager.add_to_cart(p["id"], self.category_name)).pack(
                pady=10)

        for i in range(3):
            self.products_frame.columnconfigure(i, weight=1)

    def search_item(self):
        target = self.search_var.get()
        sorted_by_name = merge_sort(self.products, key="name")
        idx = binary_search(sorted_by_name, target)
        if idx != -1:
            self.display_products([sorted_by_name[idx]])
        else:
            messagebox.showinfo("Search", "Item not found")

    def sort_products(self, reverse=False):
        sorted_list = merge_sort(self.products, key="price", reverse=reverse)
        self.display_products(sorted_list)

    def go_back(self):
        self.nav_stack.pop()

    def on_close(self):
        self.destroy()
        if self.master:
            self.master.deiconify()


class CartPage(tk.Toplevel) :
    def __init__(self, parent, cart_manager, nav_stack):
        super().__init__(parent)
        self.cart_manager = cart_manager
        self.nav_stack = nav_stack

        self.geometry('900x700')
        self.title("Shopping Cart - E-Commerce Store")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="white", relief='raised', bd=2)
        main_frame.pack(expand=True, fill="both", padx=50, pady=50)

        header_frame = tk.Frame(main_frame, bg="white", height=60)
        header_frame.pack(fill="x")

        back_button = tk.Button(header_frame, text=" ← Back ", font=("Arial", 15, "bold"),
                                fg=Purple, bg="white", relief='flat', cursor='hand2',
                                activebackground="white",
                                command=self.back_to_store)
        back_button.pack(side="left", padx=20, pady=20)

        title_label = tk.Label(main_frame, text="Shopping Cart", font=("Arial", 25, "bold"),
                               fg=Purple, bg="white")
        title_label.pack(expand=True, fill='x', pady=5)

        self.items_frame = tk.Frame(main_frame, bg="white")
        self.items_frame.pack(fill='both', expand=True, padx=15, pady=10)

        self.refresh_items()

        total_frame = tk.Frame(main_frame, bg="white", height=80)
        total_frame.pack(fill='x', side='bottom', padx=15, pady=15)

        self.total_label = tk.Label(total_frame, text=f"Total : $ {self.cart_manager.total_price}",
                                    font=("Arial", 20, "bold"), fg="#DAA520", bg="white")
        self.total_label.pack(side='left', padx=15)

        tk.Button(total_frame, text="Checkout", font=("Arial", 12),
                  fg="white", bg=Purple, relief='flat', cursor='hand2',
                  width=13, height=2, command=self.checkout).pack(side='right', padx=15)

        tk.Button(total_frame, text="Clear Cart", font=("Arial", 12),
                  fg="white", bg="#C0392B", relief='flat', cursor='hand2',
                  width=12, height=2, command=self.clear_cart).pack(side='right', padx=5)

    def refresh_items(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        if not self.cart_manager.cart:
            tk.Label(self.items_frame, text="🛒 Your cart is empty",
                     font=("Arial", 20), fg=Purple, bg="white").pack(pady=60)

            tk.Button(self.items_frame, text="Continue Shopping",
                      font=("Arial", 12), fg="white", bg=Purple,
                      relief='flat', cursor='hand2',
                      command=self.back_to_store).pack(pady=20)
        else:
            for item in self.cart_manager.cart:
                item_frame = tk.Frame(self.items_frame, bg="white", relief='raised', bd=4)
                item_frame.pack(fill='x', pady=5, padx=10)

                tk.Label(item_frame, text=f"{item['name']}", font=("Arial", 18, "bold"),
                         bg="white").pack(side='left', padx=15, pady=8)
                tk.Label(item_frame, text=f"Brand: {item.get('brand')}", font=("Arial", 12),
                         fg="gray", bg="white").pack(side='left', padx=15, pady=8)
                tk.Label(item_frame, text=f"${item['price']} x {item['quantity']}", font=("Arial", 18, "bold"),
                         fg="#DAA520", bg="white").pack(side='right', padx=15, pady=8)

                def remove_this_item(it=item):
                    self.cart_manager.remove_from_cart(it['id'], it['category'])
                    self.refresh_items()
                    self.total_label.config(text=f"Total: ${self.cart_manager.total_price}")

                tk.Button(item_frame, text="Remove", font=("Arial", 12), fg="white",
                          bg="#C0392B", relief='flat', cursor='hand2',
                          command=remove_this_item).pack(side='right', padx=5, pady=8)

    def clear_cart(self) :
        self.cart_manager.clear_cart()
        self.refresh_items()
        self.total_label.config(text=f"Total: ${self.cart_manager.total_price}")

    def checkout(self):
        result = self.cart_manager.checkout()
        messagebox.showinfo("Checkout", result)
        self.refresh_items()
        self.total_label.config(text=f"Total: ${self.cart_manager.total_price}")

    def back_to_store(self) :
        self.nav_stack.pop()

    def on_close(self) :
        self.destroy()
        if self.master :
            self.master.deiconify()


class HomePage(tk.Tk) :

    def __init__(self, cart_manager, nav_stack):
        super().__init__()
        self.cart_manager = cart_manager
        self.nav_stack = nav_stack
        self.geometry(WINDOW_SIZES['home'])
        self.title("Online Store - Categories")
        self.configure(bg=COLORS['background'])
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg=COLORS['surface'], relief='raised', bd=2)
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        tk.Label(main_frame, text="Welcome", font=("Arial", 28, "bold"), fg=COLORS['primary'],
                 bg=COLORS['surface']).pack(pady=(20, 5))
        tk.Label(main_frame, text="Explore our categories", font=FONTS['body'], fg=COLORS['text_secondary'],
                 bg=COLORS['surface']).pack(pady=(0, 20))

        top_buttons = tk.Frame(main_frame, bg=COLORS['surface'])
        top_buttons.pack(pady=10, fill="x", padx=20)

        tk.Button(top_buttons, text="Cart", font=FONTS['button'],
                  fg="white", bg=COLORS['error'], relief='flat',
                  cursor='hand2', activebackground='#C0392B',
                  width=12, height=2,
                  command=self.open_cart
                  ).pack(side="right", padx=10)

        tk.Button(top_buttons, text="Logout", font=FONTS['button'],
                  fg="white", bg=COLORS['error'], relief='flat',
                  cursor='hand2', activebackground='#C0392B',
                  width=12, height=2,
                  command=self.logout
                  ).pack(side="left", padx=10)

        categories_frame = tk.Frame(main_frame, bg=COLORS['surface'])
        categories_frame.pack(pady=20, expand=True, fill="both")

        categories = [
            ("HomeAppliances", COLORS['gray'], "Home Appliances"),
            ("Electronics", COLORS['gray'], "Electronics"),
            ("Fashion", COLORS['gray'], "Fashion"),
            ("Books", COLORS['gray'], "Books"),
            ("Sports", COLORS['gray'], "Sports")
        ]

        for idx, (cat, color, text) in enumerate(categories):
            row, col = divmod(idx, 2)
            btn = tk.Button(categories_frame, text=text, font=FONTS['heading'],
                            fg="white", bg=color,
                            relief='flat', cursor='hand2',
                            command=lambda c=cat, t=text: self.open_category(c, t))
            btn.grid(row=row, column=col, padx=20, pady=20, sticky='nsew')

        for i in range(3):
            categories_frame.rowconfigure(i, weight=1)
        for j in range(2):
            categories_frame.columnconfigure(j, weight=1)

    def logout(self):
        confirmed = messagebox.askyesno("Logout Confirmation", "Are you sure you want to logout?")
        if confirmed :
            self.cart_manager.cart = []
            messagebox.showinfo("Success", "You have been logged out successfully")
            self.destroy()
            import Login
            Login.run_login()

    def open_category(self, category, title):
        category_page = CategoryPage(self, category, title, self.cart_manager, self.nav_stack)
        self.nav_stack.push(category_page)
        self.withdraw()

    def open_cart(self):
        cart_page = CartPage(self, self.cart_manager, self.nav_stack)
        self.nav_stack.push(cart_page)
        self.withdraw()

    def on_close(self):
        self.destroy()


def pages_manager_fun() :
    nav_stack = Stack()
    cart_manager = CartManager()
    home_page = HomePage(cart_manager, nav_stack)
    nav_stack.push(home_page)
    home_page.mainloop()

if __name__ == "__main__" :
    pages_manager_fun()