"""Contiene a la clase Carta"""
import flet
from producto import MenuProducto, Producto, Fila

class Carta():
    """
    Tiene los métodos necesarios para crear una lista con
    todos los productos y seleccionar cantidades cada uno.
    
    Variables de clase:
    productos: lista de los productos seleccionados por el usuario
    tabs: el meú para filtrar los platos que se muestran
    lv: una lista con todos los productos disponibles para la categoría actual
    """
    def __init__(self, productos: list[Producto]) -> None:
        self.productos:list[Producto | MenuProducto] = productos

    def cargar_vista(self, page:flet.Page, navegacion:flet.NavigationBar) -> flet.View:
        """
        Inicializa una lista con los productos y un botón continuar,
        los añade a una vista y la envía.

        :param page: La pagina para crear las filas de la vista.
        :param navegacion: Una barra de navegación para añadir a la interfaz.
        :returns: Una vista con la lista y el botón.
        """

        self.tabs:flet.Tabs = flet.Tabs(
                tabs=[
                    flet.Tab(
                        text="Todo",
                        content=flet.ListView(spacing=10, expand=True)
                    ),
                    flet.Tab(
                        text="Primeros",
                        content=flet.ListView(spacing=10, expand=True)
                    ),
                    flet.Tab(
                        text="Segundos",
                        content=flet.ListView(spacing=10, expand=True)
                    ),
                    flet.Tab(
                        text="Postres",
                        content=flet.ListView(spacing=10, expand=True)
                    ),
                    flet.Tab(
                        text="Bebidas",
                        content=flet.ListView(spacing=10, expand=True)
                    ),
                    flet.Tab(
                        text="Otros",
                        content=flet.ListView(spacing=10, expand=True)
                    ),
                ],
            expand=1,
            selected_index=0,
            on_change=lambda _: self.cambiar_filtro(page))

        vista = flet.View( "/", navigation_bar=navegacion,
                        padding=flet.padding.only(top=45, left=10))

        vista.controls=[self.tabs]

        return vista

    def cambiar_filtro(self, page:flet.Page):
        """Carga la tabla con los productos apropiados.
        
        :param page: Se actualiza cuando los datos se han cargado."""
        indice = self.tabs.selected_index
        tab:flet.Tab = self.tabs.tabs[indice]
        self.lv:flet.ListView = tab.content
        if indice==0:
            self.cargar_productos(page)
        elif indice==1:
            self.cargar_productos(page, "Primeros")
        elif indice==2:
            self.cargar_productos(page, "Segundos")
        elif indice==3:
            self.cargar_productos(page, "Postres")
        elif indice==4:
            self.cargar_productos(page, "Bebidas")
        elif indice==5:
            self.cargar_productos(page, "Otro")
        page.update()

    def cargar_productos(self, page:flet.Page, filtro:str | None = None) -> None:
        """
        Añade a una lista los productos, cada uno con dos botones y
        un campo de texto para seleccionar la cantidad.

        :param filtro: Se cargan solo los productos que tengan este str en el atributo menu.
                    Si está vacío, se cargan todos.
        :param page: La página que se usará para crear los objetos Fila.
        """
        self.lv.controls.clear()
        for producto in self.productos:
            if isinstance(producto, Producto):
                if producto.nombre != "Menu 1" :
                    if filtro is None:
                        fila = Fila(page, producto)
                        self.lv.controls.append(fila.crear_fila())
                    elif producto.menu==filtro:
                        fila = Fila(page, producto)
                        self.lv.controls.append(fila.crear_fila())
