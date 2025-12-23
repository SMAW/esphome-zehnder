import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import fan, spi
from esphome.const import CONF_ID
from esphome import pins

DEPENDENCIES = ["spi"]

# Define custom pin constants for CC1101
CONF_GDO0_PIN = "gdo0_pin"
CONF_GDO2_PIN = "gdo2_pin"
CONF_CS_PIN = "cs_pin"

zehnder_fan_ns = cg.esphome_ns.namespace("zehnder_fan")
ZehnderFanComponent = zehnder_fan_ns.class_("ZehnderFanComponent", fan.Fan, cg.PollingComponent)

CONFIG_SCHEMA = (
    fan.fan_schema(ZehnderFanComponent)
    .extend(
        {
            cv.GenerateID(): cv.declare_id(ZehnderFanComponent),
            cv.Required(CONF_CS_PIN): pins.gpio_output_pin_schema,
            cv.Required(CONF_GDO0_PIN): pins.gpio_input_pin_schema,
            cv.Optional(CONF_GDO2_PIN): pins.gpio_input_pin_schema,
            cv.Required(spi.CONF_SPI_ID): cv.use_id(spi.SPIComponent),
        }
    )
    .extend(cv.polling_component_schema("1s"))
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await fan.register_fan(var, config)

    # Set SPI parent
    spi_parent = await cg.get_variable(config[spi.CONF_SPI_ID])
    cg.add(var.set_spi_parent(spi_parent))

    # Register CC1101 pins
    cs_pin = await cg.gpio_pin_expression(config[CONF_CS_PIN])
    cg.add(var.set_cs_pin(cs_pin))
    
    gdo0_pin = await cg.gpio_pin_expression(config[CONF_GDO0_PIN])
    cg.add(var.set_gdo0_pin(gdo0_pin))
    
    if CONF_GDO2_PIN in config:
        gdo2_pin = await cg.gpio_pin_expression(config[CONF_GDO2_PIN])
        cg.add(var.set_gdo2_pin(gdo2_pin))
