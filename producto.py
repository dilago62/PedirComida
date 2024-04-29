"""Contiene las clases Producto, MenuProducto y Fila"""
from typing_extensions import Self
import flet
import variables


class Producto():
    """
    Guarda los datos de un producto.
    """
    seleccionado:int = 0
    imagen:str = variables.NO_IMAGEN

    def __init__(self, nombre:str | None = None, id_producto:int | None = None,
                precio:float | None = None, menu:str | None = None,
                descripcion:str | None = None, producto:Self | None = None) -> None:
        """
        Si recibe un producto, ignora el resto de datosrecibidos y crea un
        producto con los atributos mínimos para hacer un envío de datos.
        """
        if producto is None:
            self.nombre:str = nombre
            self.precio:float = precio
            self.id_producto:int = id_producto
            self.menu:str = menu
            self.descripcion:str = descripcion
        else:
            self.nombre:str = producto.nombre
            self.precio:float = producto.precio
            self.id_producto:int = producto.id_producto
            self.seleccionado = producto.seleccionado


    def calcular_total(self) -> None:
        """
        Multiplica precio por seleccionado y lo almacena en total.
        """
        self.total:float=self.seleccionado*self.precio

class MenuProducto():
    """
    Almacena unos productos, agrupádolos para formar un menú.
    """
    def __init__(self, primero:Producto, segundo:Producto,
                bebida:Producto, postre:Producto) -> None:
        self.primero:Producto = primero
        self.segundo:Producto = segundo
        self.postre:Producto = postre
        self.bebida:Producto = bebida

    def get_info(self) -> str:
        """
        Crea un str con el precio total y los nombres de los productos que componen este menú.

        :returns: El str creado.
        """
        info = "Menu:\n"
        info += "Primero: "+self.primero.nombre+"\n"
        info += "Segundo: "+self.segundo.nombre+"\n"
        info += "Postre: "+self.postre.nombre+"\n"
        info += "Bebida: "+self.bebida.nombre+"\n"
        return info

    def get_dimis(self, productos:list[Producto | Self], page:flet.Page) -> flet.Dismissible:
        """
        Crea un objeto eliminable con la información de el objeto. Si el objeto es eliminado,
        también lo es de la lista recibida.

        :param productos: La lista de la qe será eliminado.
        :param page: La pagina para mostrar la informacion del menú.
        :returns: El objeto eliminable con la información propia.
        """
        return flet.Dismissible(content=flet.ElevatedButton(text="Menu:\n"
                +self.primero.nombre+" - "
                +self.segundo.nombre+" - "
                +self.postre.nombre+" - "
                +self.bebida.nombre,
                icon=flet.icons.INFO,
                color=flet.colors.BLACK, bgcolor=flet.colors.TRANSPARENT,
                icon_color=flet.colors.BLUE, elevation=0,
                on_click=lambda _:self.mostrar_info(page),
                style=flet.ButtonStyle(shape=flet.RoundedRectangleBorder(radius=0))),
            dismiss_direction=flet.DismissDirection.HORIZONTAL,
            background=flet.Container(bgcolor=flet.colors.RED_300),
            secondary_background=flet.Container(bgcolor=flet.colors.RED_300),
            on_dismiss=lambda _: self.eliminar_menu(productos))

    def eliminar_menu(self, productos:list[Producto | Self]) -> None:
        """
        Elimina al propio menú de la lista de productos recibida y
        disminuye en uno los menus seleccionados.

        :param productos: La lista de la que será eliminado.
        """
        productos.remove(self)
        for item in productos:
            if isinstance(item, Producto):
                if item.nombre == "Menu 1":
                    item.seleccionado -= 1

    def mostrar_info(self, page:flet.Page) -> None:
        """
        Muestra un aviso con la infformacion del menú.

        :param page: La página sobre la que se muestra el aviso.
        """
        page.dialog = flet.AlertDialog(title= flet.Text("Menu:"),
            content=flet.Text(self.primero.descripcion+"\n"
                            +self.segundo.descripcion+"\n"
                            +self.postre.descripcion+"\n"
                            +self.bebida.descripcion), open=True)
        page.update()

class Fila():
    """
    Crea objetos fila para añadir a listas.
    """
    def __init__(self, page:flet.Page, producto:Producto) -> None:
        self.page:flet.Page=page
        self.producto:Producto=producto

    def crear_fila(self) -> flet.Row:
        """
        Añade a una fila un texto y una fila que contiene botones
        para seleccionar una cantidad de un producto.
        
        :returns: Un objeto row con texto y los botones y el indicador de
        la cantidad seleccionada, vinculado a un producto.
        """
        self.tf:flet.TextField = flet.Text(self.producto.seleccionado,
                            text_align=flet.TextAlign.CENTER, width=45, height=45,
                            theme_style=flet.TextThemeStyle.HEADLINE_LARGE)

        self.imagen: flet.Image = flet.Image(src_base64=self.producto.imagen, width=80,
                                height=80, fit=flet.ImageFit.FIT_HEIGHT)
        tx = flet.Text(self.recortar(self.producto.nombre.upper()), weight=flet.FontWeight.BOLD)
        tx2 = flet.Text(str(round(self.producto.precio, 2))+"€")
        ibmen = flet.IconButton(icon=flet.icons.REMOVE,
                                icon_color=flet.colors.RED, on_click=lambda _:self.click_menos(), )
        ibmas = flet.IconButton(flet.icons.ADD, on_click=lambda _:self.click_mas())
        ibinfo = flet.IconButton(flet.icons.INFO, on_click=lambda _:self.mostrar_info())

        row2 = flet.Row(
            controls=[
                ibinfo,
                ibmen,
                flet.Container(self.tf, border=flet.border.all(1, flet.colors.BLACK),
                                alignment=flet.alignment.center),
                ibmas
        ],expand=5)

        row1 = flet.Row(
            controls=[
                self.imagen,
                flet.Column(
                    [
                        tx,
                        tx2
                    ]
                )
        ],expand=4)

        r = flet.Row(
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
            controls=[
                row1,
                row2
        ])
        return r

    def click_menos(self) -> None:
        """
        Reduce la cantidad seleccionada de un producto si es mayor que cero. Actualiza la vista.
        """
        if self.producto.seleccionado>0:
            self.producto.seleccionado-=1
            self.tf.value = self.producto.seleccionado
            self.page.update()

    def click_mas(self) -> None:
        """
        Aumenta la cantidad seleccionada de un producto. Actualiza la vista.
        """
        self.producto.seleccionado+=1
        self.tf.value = self.producto.seleccionado
        self.page.update()

    def mostrar_info(self) -> None:
        """Muestra la descripcion del objeto vinculado."""
        self.page.dialog = flet.AlertDialog(title= flet.Text(self.producto.nombre),
            content=flet.Text(self.producto.descripcion), open=True)
        self.page.update()

    def recortar(self, original:str) -> str:
        """
        Ajusta el tamaño de un str. Si es menor o igual que 10 no lo
        cambia. Si es mayor lo reduce a siete y añade tres puntos.

        :param original: el str que se va a probar a reducir.
        :returns: el str original o una versión reducida si era mayor de 10.
        """
        if len(original) >10:
            return original[0:7]+"..."
        return original
