"""Contiene la clase Pago"""
import json
from datetime import datetime, timedelta
import flet
import requests
from producto import Producto, MenuProducto
import variables


class Pago():
    """
    Tiene los métodos necesarios para iniciar la patalla final,
    probar los datos y enviar la información.
    
    Variables de clase:
    precio: valor recibido con el precio total de los productos
    page: pagina, para actualizar y colocar los componentes
    productos: lista de los productos seleccionados por el usuario
    drop: desplegable para seleccionar día y hora de recogida
    tel: campo de texto para el teléfono del usuario
    notas: campo de texto para que el usuario las añada al pedido
    """

    def __init__(self, precio: float, page:flet.Page,
                productos:list[Producto | MenuProducto]) -> None:
        self.precio:float = precio
        self.page:flet.Page = page
        self.productos:list[Producto | MenuProducto] = productos

    def cargar_vista(self, total:float, navigacion:flet.NavigationBar) -> None:
        """
        Crea una vista para elegir hora de recogida, añadir un teléfono de contacto y
        notas, mostrar el precio y botones de continuar y volver.

        :param total: Para mostrar en el método confirmar.
        :param navigacion: Una barra de navegación para añadir a la interfaz.
        """
        self.drop:flet.Dropdown = flet.Dropdown(label="Hora de recogida", alignment=flet.alignment.center)
        self.tel:flet.TextField = flet.TextField(label="Teléfono de contacto", prefix_text="+34 ",
                                input_filter=flet.NumbersOnlyInputFilter(),
                                max_length=9, keyboard_type=flet.KeyboardType.PHONE)
        self.notas:flet.TextField = flet.TextField(label="Anotaciones", multiline=True)
        confirmar = flet.FilledButton("Confirmar pedido",
                                on_click=lambda _:self.confirmar(total))
        self.cargar_dropdown()

        vista= flet.View("/confirmar",
            [
                self.drop,
                self.tel,
                self.notas,
                flet.Row([confirmar], alignment=flet.MainAxisAlignment.CENTER,
                vertical_alignment=flet.CrossAxisAlignment.CENTER,)
            ],
            horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            padding=flet.padding.only(top=45, left=10, right=10),
            navigation_bar=navigacion
        )
        return vista

    def confirmar(self, total:float) -> None:
        """
        Llama a validar. Si es correcto llama a comprobar,
        si no envía al usuario a la primera vista.
        
        :param total: El precio final para comprobar.
        """
        if self.validar():
            self.comprobar(total)
        else:
            self.page.dialog.on_dismiss=lambda _:self.page.go("/")

    def productos_envio(self) -> list[Producto | MenuProducto]:
        """
        Crea una copia de la variable de clase productos con el total
        de cada objeto que se debe preparar y el precio final de cada cosa.

        :returns: La lista creada por este método.
        """
        envio_p:list[Producto] = []
        envio_m:list[MenuProducto] = []
        for item in self.productos:
            if isinstance(item, Producto):
                productos_pedido = Producto(producto=item)
                envio_p.append(productos_pedido)
                productos_pedido.calcular_total()
            else:
                envio_m.append(item)
        for menu in envio_m:
            for productos_pedido in envio_p:
                if productos_pedido.nombre == menu.primero.nombre:
                    productos_pedido.seleccionado += 1
                elif productos_pedido.nombre == menu.segundo.nombre:
                    productos_pedido.seleccionado += 1
                elif productos_pedido.nombre == menu.postre.nombre:
                    productos_pedido.seleccionado += 1
                elif productos_pedido.nombre == menu.bebida.nombre:
                    productos_pedido.seleccionado += 1
        return envio_p + envio_m

    def preparar(self, total:float) -> None:
        """
        Transforma la lista de productos a un json parra enviarlos.
        
        :param total: El precio total del pedido.
        """
        productos_pedido = self.productos_envio()
        recogida = self.get_recogida()
        print(recogida)
        transformado = {}
        products = []
        for producto in productos_pedido:
            if isinstance(producto, Producto):
                if producto.seleccionado>0:
                    guardar = {"product_id":producto.id_producto,
                                "name":producto.nombre,
                                "price_unit":producto.precio,
                                "qty":producto.seleccionado,
                                "price_subtotal": producto.total,
                                "price_subtotal_incl": producto.total}
                    products.append(guardar)
        transformado["products"] = products
        transformado["total"] = total
        transformado["client_phone"] = self.tel.value
        transformado["date_order"] = recogida
        transformado["notes"] = self.notas.value
        resultado = json.dumps(transformado)
        if requests.post(variables.PEDIDO, data=resultado, timeout=20).ok:
            self.page.dialog = flet.AlertDialog(title= flet.Text("Pedido realizado"),
                                content=flet.Text("Su pedido se ha hecho correctamente"), open=True,
                                on_dismiss=lambda _:self.page.go("/"))
        else:
            self.page.dialog = flet.AlertDialog(title= flet.Text("Ha ocurrido un error"),
                                content=flet.Text("Su pedido no ha podido realizarse"), open=True,
                                on_dismiss=lambda _:self.page.go("/"))
        self.limpiar_productos()
        self.page.update()
        
    def limpiar_productos(self) -> None:
        """
        Vacia la lista de menús y establece la cantidad seleccionada de cada producto a cero.
        """ 
        copia = []
        for item in self.productos:
            if isinstance(item, Producto):
                item.seleccionado=0
                copia.append(item)
        self.productos.clear()
        self.productos = copia

    def comprobar(self, total) -> None:
        """
        Muestra los productos seleccionados. Ofrece continuar con el pedido o volver.

        :param total: El precio total ya calculado.
        """
        mensaje = ""
        for item in self.productos:
            if isinstance(item, Producto):
                if item.seleccionado>0:
                    precio = item.precio*item.seleccionado
                    mensaje+=str(item.seleccionado) + " - " + item.nombre
                    mensaje+="      " + str(precio) + "\n"
            elif isinstance(item, MenuProducto):
                mensaje += item.get_info()
        mensaje+="Total: " + str(total)
        alerta = flet.AlertDialog(modal=True, title=flet.Text("Productos seleccionados"),
                                content=flet.Text(mensaje) , open=True,  actions=[
                                flet.TextButton("Continuar",
                                                on_click=lambda _: self.preparar(total)),
                                flet.TextButton("Volver",
                                                on_click=lambda _: self.page.go("/")),
                ],)
        self.page.dialog = alerta
        self.page.update()

    def validar(self) -> bool:
        """
        Comprueba si hay productos seleccionados, un teléfono de contacto y
        hora de recogida. Muestra un aviso si no se cumplen estas condiciones.
        
        :returns: True, si todos los datos están; False si no.
        """
        errores: str = ""

        if self.drop.value is None:
            errores+="No se ha selecionado una hora de recogida\n"

        if self.tel.value=="":
            errores+="No se ha introducido un teléfo\n"
        elif len(self.tel.value)!=9:
            errores+="No se ha introducido el teléfono completo\n"

        if self.precio==0.0:
            errores+="No se han seleccionado productos"

        if errores!="":
            alerta = flet.AlertDialog(modal=False, title=flet.Text(
                "Se han producido los siguientes errores"), content=flet.Text(errores), open=True)
            self.page.dialog = alerta
            self.page.update()
            return False

        return True

    def get_recogida(self) -> str:
        """
        Devuelve la fecha y hora de recogida selecionadas del pedido.
        
        :returns: un str con la fecha y hora. Formato yyyy-mm-dd hh:mm:ss
        """
        for option in self.drop.options:
            if self.drop.value == option.key:
                return str(option.data)+":00"
        return None

    def cargar_dropdown(self) -> None:
        """
        Permite seleccionar una hora y minuto cargándolo cada 15 minutos,
        desde la hora actual al cierre.
        """
        ahora = datetime.now()
        ahora += timedelta(days=1)
        cierre = datetime(minute=00, hour=2, day=ahora.day, year=ahora.year, month=ahora.month)
        avance = 15

        hora = datetime.now()
        hora.replace(second=0)
        while (hora.minute%avance)!=0:
            hora+=timedelta(minutes=1)
        while(hora < cierre):
            self.drop.options.append(
                    flet.dropdown.Option(hora.strftime("%H:%M"), alignment=flet.alignment.center,data=hora.strftime("%Y-%m-%d %H:%M")))
            hora += timedelta(minutes=avance)
