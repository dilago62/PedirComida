"""Contiene la clase Menu"""
import flet
from producto import Producto, MenuProducto

class Menu():
    """
    Tiene los métodos necesarios para crear una pantalla de menú
    y guardarlo para hacer un pedido.
    """
    def __init__(self, productos:list[Producto | MenuProducto]) -> None:
        self.productos:list[Producto | MenuProducto] = productos

    def cargar_vista(self, page:flet.Page, navegacion:flet.NavigationBar) -> flet.View:
        """
        Crea una vista para seleccionnar los productos de un menu, guardarlos y eliminar menús.

        :param page: La pagina para crear las filas de la vista.
        :param navegacion: Una barra de navegación para añadir a la interfaz.
        :returns: Una vista con los dropdown, un botn y la barra de navegación.
        """
        self.dw1:flet.Dropdown = flet.Dropdown(label="Primero")
        self.dw2:flet.Dropdown = flet.Dropdown(label="Segundo")
        self.dwp:flet.Dropdown = flet.Dropdown(label="Postre")
        self.dwb:flet.Dropdown = flet.Dropdown(label="Bebida")

        self.lv:flet.ListView = flet.ListView(auto_scroll=True, expand=True)
        self.actualizar_menus(page)

        anhadir = flet.FilledButton("Añadir al pedido",
                                on_click=lambda _: self.anhadir_menu(page))

        txt = flet.Text("Menús seleccionados:", theme_style=flet.TextThemeStyle.HEADLINE_MEDIUM)

        self.cargar_opcion_menu(self.dw1, "Primeros")
        self.cargar_opcion_menu(self.dw2, "Segundos")
        self.cargar_opcion_menu(self.dwp, "Postres")
        self.cargar_opcion_menu(self.dwb, "Bebidas")

        vista = flet.View("/menu",
            [
            self.dw1,
            self.dw2,
            self.dwp,
            self.dwb,
            anhadir,
            flet.Divider(),
            txt,
            self.lv
            ],
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
            horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            padding=flet.padding.only(top=45, left=10, right=10),
            navigation_bar=navegacion,
            scroll="allways")
        return vista

    def actualizar_menus(self, page:flet.Page) -> None:
        """
        Carga todos los menús de productos como objetos eliminables en una lista

        :param page: Pagina para mostrar la informacion del menú añadido.
        """
        self.lv.controls.clear()
        for menu in self.productos:
            if isinstance(menu, MenuProducto):
                self.lv.controls.append(menu.get_dimis(self.productos, page))

    def cargar_opcion_menu(self, dw:flet.Dropdown, menu:str) -> None:
        """
        Carga todos los productos en un dropdown con el apartado menu igual al str introducido.

        :param dw: el dropdown donde se cargan los productos.
        :param menu: el texto que deben tener en menu los productos que se quiere cargar.
        """
        for producto in self.productos:
            if isinstance(producto, Producto):
                if producto.menu == menu:
                    dw.options.append(flet.dropdown.Option(producto.nombre))

    def recuperar_producto(self, dw:flet.Dropdown) -> Producto:
        """
        Obtiene el objeto producto seleccionado en un dropdown.
        
        :param dw: el dropdown para buscar el producto.
        :returns: el producto con el nombre correspondiente.
        """
        for producto in self.productos:
            if isinstance(producto, Producto):
                if producto.nombre == dw.value:
                    return producto
        return None

    def anhadir_menu(self, page:flet.Page) -> None:
        """
        Obtiene los productos seleccionados y crea un menú de productos con ellos si están todos.Si
        no, muestra un mensaje de aviso.
        
        :param page: La página sobre la que se actua y que se modifica.
        """
        p = self.recuperar_producto(self.dw1)
        s = self.recuperar_producto(self.dw2)
        po = self.recuperar_producto(self.dwp)
        b = self.recuperar_producto(self.dwb)
        if p is None or s is None or po is None or b is None:
            page.dialog = flet.AlertDialog(title= flet.Text("No se ha guardado el menú."),
                                content=flet.Text("Selecciona un primero, " +
                                                "un seundo, un postre y una bebida."), open=True)
            page.update()
        else:
            for producto in self.productos:
                if isinstance(producto, Producto):
                    if producto.nombre == "Menu 1":
                        menu_p = producto
            menu_p.seleccionado += 1
            menu = MenuProducto(p, s, b, po)
            self.productos.append(menu)
            self.actualizar_menus(page)
            page.update()
