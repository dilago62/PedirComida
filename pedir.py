"""Contiene la clase Pago"""
import json
from datetime import datetime, timedelta
import time
import flet
import requests
from producto import Producto, MenuProducto
import variables


class Pago():
    """
    Tiene los métodos necesarios para iniciar la patalla final,
    probar los datos y enviar la información.
    """

    drop: flet.Dropdown
    tel: flet.TextField
    precio: float
    notas: flet.TextField
    page: flet.Page
    productos:list[Producto | MenuProducto]
    manhana:bool = False


    def __init__(self, precio: float, page:flet.Page,
                productos:list[Producto | MenuProducto]) -> None:
        self.precio = precio
        self.page = page
        self.productos = productos

    def cargar_vista(self, total:float, navigacion:flet.NavigationBar) -> None:
        """
        Crea una vista para elegir hora de recogida, añadir un teléfono de contacto y
        notas, mostrar el precio y botones de continuar y volver.

        :param total: Para mostrar en el método confirmar.
        :param navigacion: Una barra de navegación para añadir a la interfaz.
        """
        self.drop = flet.Dropdown(label="Hora de recogida")
        self.tel = flet.TextField(label="Teléfono de contacto", prefix_text="+34 ",
                                input_filter=flet.NumbersOnlyInputFilter(),
                                max_length=9, keyboard_type=flet.KeyboardType.PHONE)
        self.notas = flet.TextField(label="Anotaciones", multiline=True)
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
            self.page.go("/")

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
        """
        productos_pedido = self.productos_envio()
        recoger = datetime.now()
        if self.manhana:
            recoger += timedelta(1)
        recogida = recoger.strftime("%Y-%m-%d")
        recogida += " " + self.drop.value + ":00"
        transformado = {}
        products = []
        for producto in productos_pedido:
            if isinstance(producto, Producto):
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
                                content=flet.Text("Su pedido se ha hecho correctamente"), open=True)
        else:
            self.page.dialog = flet.AlertDialog(title= flet.Text("Ha ocurrido un error"),
                                content=flet.Text("Su pedido no ha podido realizarse"), open=True)
        for item in self.productos:
            print(type(item))
            if isinstance(item, Producto):
                item.seleccionado=0
            elif isinstance(item, MenuProducto):
                self.productos.remove(item)
        self.page.update()

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

    def cargar_dropdown(self) -> None:
        """
        Permite seleccionar una hora y minuto cargándolo cada 15 minutos,
        desde la hora actual al cierre.
        """

        cierre = 2
        avance = 15
        continuar:bool = True

        h_actual = time.time()
        h_local = time.localtime(h_actual)
        h_num = time.strftime("%H:%M", h_local)
        h_split=h_num.split(":")
        h=int(h_split[0])
        minutos = int(h_split[1])

        while (minutos%avance)!=0:
            minutos+=1
            if minutos == 60:
                minutos = 00
        while h!=cierre:
            while minutos!=0 | continuar:
                self.drop.options.append(
                    flet.dropdown.Option(str(h).zfill(2)+":"+str(minutos).zfill(2)))
                minutos+=avance
                if minutos >= 60:
                    minutos = 00
                    continuar=False
            h+=1
            continuar=True
            if h == 24:
                h = 0
                self.manhana = True
