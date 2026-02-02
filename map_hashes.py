from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class BattleType(str, Enum):
    AIR = "air"
    GROUND = "ground"
    NAVAL = "naval"
    AIR_IN_GROUND = "air_in_ground"
    AIR_IN_NAVAL = "air_in_naval"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class MapInfo:
    map_id: str
    display_name: str
    battle_type: BattleType
    dimensions: Optional[Dict[str, int]] = None


AIR_MAPS = {
    "3a6b992635cb471d0d435eec3f28ee815d832f0a6666412ac6dce2e80": MapInfo(map_id="air_afghan_map", display_name="✈️ Afghan", battle_type=BattleType.AIR),
    "15ee03fc1ff41ec8be666cc5d379e73517188c68dea2bc373878ca368": MapInfo(map_id="air_africa_desert_map", display_name="✈️ Africa Desert", battle_type=BattleType.AIR),
    "766d989f56368aece619d13226548d001a5049f0a7616dc627c20d008": MapInfo(map_id="air_denmark_map", display_name="✈️ Denmark", battle_type=BattleType.AIR),
    "84b881b90df00ff01fc817c41f01bc01e281c8a7e2ac41280900080c0": MapInfo(map_id="air_equatorial_island_map", display_name="✈️ Equatorial Island", battle_type=BattleType.AIR),
    "33eca388d30193c3924790b780fd14d593ad69ced193e26387070a0c0": MapInfo(map_id="air_grand_canyon_map", display_name="✈️ Grand Canyon", battle_type=BattleType.AIR),
    "50465019202400c101010542408043818e019c83090e34884110c30c8": MapInfo(map_id="air_israel_map", display_name="✈️ Israel", battle_type=BattleType.AIR),
    "6e07bca6e1d3c6229c263448a892d1632706941cf01fc09e03b206588": MapInfo(map_id="air_kamchatka_map", display_name="✈️ Kamchatka", battle_type=BattleType.AIR),
    "5846f888f80af84bec93589f60f2ca22738e14cd1d483a20b45509880": MapInfo(map_id="air_ladoga_map", display_name="✈️ Ladoga", battle_type=BattleType.AIR),
    "5123690174805c84e29c359912da835b2b452112646cf0e843928e4b0": MapInfo(map_id="air_mysterious_valley_map", display_name="✈️ Mysterious Valley", battle_type=BattleType.AIR),
    "4a3030084983bf387c5ba1c6850d9893629407aa0b88270ea3a657bf0": MapInfo(map_id="air_normandy_map", display_name="✈️ Normandy", battle_type=BattleType.AIR),
    "58123934a09b144356a418d915b03b28db823a2ba389265826e2a4690": MapInfo(map_id="air_pyrenees_map", display_name="✈️ Pyrenees", battle_type=BattleType.AIR),
    "2a114c100eb07a408e433dc1e1e253c25606bc09f912618cf319a4820": MapInfo(map_id="air_race_phiphi_islands_map", display_name="✈️ Race Phiphi Islands", battle_type=BattleType.AIR),
    "c50f091356a26e6cc8db20b609b4537990e331d6618e431ca6b98d330": MapInfo(map_id="air_skyscraper_city_map", display_name="✈️ Skyscraper City", battle_type=BattleType.AIR),
    "102cc0d3c545c1cb13261f281e4c18c3a5078024c0e9b3c423104cc00": MapInfo(map_id="air_smolensk_map", display_name="✈️ Smolensk", battle_type=BattleType.AIR),
    "63990ebec53783d5825d94bb9b23accfcd0790e360b30544cd0b07608": MapInfo(map_id="air_southeastern_cliffs_map", display_name="✈️ Southeastern Cliffs", battle_type=BattleType.AIR),
    "c645b626e88ccd21a328c60384049c13701fd03f00210000000080020": MapInfo(map_id="air_south_eastern_city_map", display_name="✈️ South Eastern City", battle_type=BattleType.AIR),
    "2eba056c2f7ca693662cc45108e89cd0df40ff016306c08c92190d1a0": MapInfo(map_id="air_vietnam_map", display_name="✈️ Vietnam", battle_type=BattleType.AIR),
}

GROUND_MAPS = {
    "2a42552469888e3091a113c4230a861b4e7958312a489687084430690": MapInfo(map_id="avg_abandoned_factory_tankmap", display_name="🚜 Abandoned Factory", battle_type=BattleType.GROUND),
    "932c3b5b5aa14cf5c7ff66dc47a62f3d2f2c683c55dd45644758da288": MapInfo(map_id="avg_abandoned_town_tankmap", display_name="🚜 Abandoned Town", battle_type=BattleType.GROUND),
    "d265b19ba67427394ebe125f5567086f16a71959c26958e999d4e59a0": MapInfo(map_id="avg_africa_desert_tankmap", display_name="🚜 Africa Desert", battle_type=BattleType.GROUND),
    "acae989d893a9a7174e2b6457680ed15de1bfc5579cb730b6e27c94f8": MapInfo(map_id="avg_alaska_town_tankmap", display_name="🚜 Alaska Town", battle_type=BattleType.GROUND),
    "b71e46f98d9133946f2c6c78e861b9c665830f0d3a3536776696e72b0": MapInfo(map_id="avg_american_valley_tankmap", display_name="🚜 American Valley", battle_type=BattleType.GROUND),
    "716ac8c5b750ad5adc34728b551e13bc8ef11cd9b9ab73c56ed96d938": MapInfo(map_id="avg_aral_sea_tankmap", display_name="🚜 Aral Sea", battle_type=BattleType.GROUND),
    "4b18aa6115e64dca8f945b4625523630fee0e98bda0774a6cd5489ac8": MapInfo(map_id="avg_arctic_tankmap", display_name="🚜 Arctic", battle_type=BattleType.GROUND),
    "383ab9ef565ae3331caeb7185924b9a6b054e35586951d2edaacace98": MapInfo(map_id="avg_ardennes_snow_tankmap", display_name="🚜 Ardennes Snow", battle_type=BattleType.GROUND),
    "381ed16f565ae53b1eaeb758792cb8a69154a35596911d2e5afcace98": MapInfo(map_id="avg_ardennes_tankmap", display_name="🚜 Ardennes", battle_type=BattleType.GROUND),
    "914cb995cb169c8845b34a84cc2192c5846b98a54dc6585ab87559230": MapInfo(map_id="avg_berlin_tankmap", display_name="🚜 Berlin", battle_type=BattleType.GROUND),
    "f169c55310971598abc45bc2a5c16b48ad4caf4e5f51db615386d99c8": MapInfo(map_id="avg_breslau_tankmap", display_name="🚜 Breslau", battle_type=BattleType.GROUND),
    "d909fa6696cc1e9127a8e740e601ec83b809721af017d43544af8c458": MapInfo(map_id="avg_container_port_tankmap", display_name="🚜 Container Port", battle_type=BattleType.GROUND),
    "b67e927e7898e312a8b9316a66d791b371d00c348a119d29b7d669198": MapInfo(map_id="avg_eastern_europe_tankmap", display_name="🚜 Eastern Europe", battle_type=BattleType.GROUND),
    "b3628d89b37141d26df493ef75cd4b01975beeb5dd8bc436ca234a438": MapInfo(map_id="avg_egypt_sinai_tankmap", display_name="🚜 Egypt Sinai", battle_type=BattleType.GROUND),
    "6ca0ed414278e4fdd1f8b3e2b7e66ac64d911f96a925e64691a5070a8": MapInfo(map_id="avg_european_fortress_tankmap", display_name="🚜 European Fortress", battle_type=BattleType.GROUND),
    "3731b8f6136c487805e097c527805f049801a0053009082490f021910": MapInfo(map_id="avg_finland_tankmap", display_name="🚜 Finland", battle_type=BattleType.GROUND),
    "904f04e81a9023b102e40f883e107c01f007591f325ca3f887f11f860": MapInfo(map_id="avg_fulda_tankmap", display_name="🚜 Fulda", battle_type=BattleType.GROUND),
    "48ce196cb0caad90c72436d2ad85455a9b673637e4e19a736994c6318": MapInfo(map_id="avg_greece_tankmap", display_name="🚜 Greece", battle_type=BattleType.GROUND),
    "f97c7bbcea78ea321a26a742399d2b1156ab3184d0c999b9f155d0590": MapInfo(map_id="avg_guadalcanal_tankmap", display_name="🚜 Guadalcanal", battle_type=BattleType.GROUND),
    "487223c5e5b30662794961cb6f1e9c7f38f720f723e9cf32198424e00": MapInfo(map_id="avg_hurtgen_tankmap", display_name="🚜 Hurtgen", battle_type=BattleType.GROUND),
    "1e2ec457487801b00362035c948523071e06a4051800f00e000000000": MapInfo(map_id="avg_iberian_castle_tankmap", display_name="🚜 Iberian Castle", battle_type=BattleType.GROUND),
    "f39f326f6c7ef0f7f236e0ed513395b6a1234f452c6416cdeccb9b3c8": MapInfo(map_id="avg_ireland_tankmap", display_name="🚜 Ireland", battle_type=BattleType.GROUND),
    "6e9c9d71bee3dd837e0b7c4edc1db8ba7938f433b97f73d6c6ee8acd8": MapInfo(map_id="avg_israel_tankmap", display_name="🚜 Israel", battle_type=BattleType.GROUND),
    "4f271f013618e7158c831da629d93a31caf895c83b0928b711a6591a0": MapInfo(map_id="avg_japan_tankmap", display_name="🚜 Japan", battle_type=BattleType.GROUND),
    "73446f597859e32b8cdb127555666ad07741aadab566c685a168f8d80": MapInfo(map_id="avg_karantan_tankmap", display_name="🚜 Karantan", battle_type=BattleType.GROUND),
    "24cd28bf0e5459b99a7394f4af6bfcd2bc3d3a3ddeb37c4f3cf189f98": MapInfo(map_id="avg_karelia_forest_a_tankmap", display_name="🚜 Karelia Forest A", battle_type=BattleType.GROUND),
    "817f02df07bccb951d0ab812cb83b68f3b9c97597ff0be2c58d9a28d8": MapInfo(map_id="avg_karpaty_passage_tankmap", display_name="🚜 Karpaty Passage", battle_type=BattleType.GROUND),
    "882334407a02a2005620a018c4d929da93c987eb077a0fc81d78164c0": MapInfo(map_id="avg_korea_lake_tankmap", display_name="🚜 Korea Lake", battle_type=BattleType.GROUND),
    "c7838f873f1c7231c4b3cb6f20fe13f867fb4ff68ff21f267e04f01b8": MapInfo(map_id="avg_krymsk_tankmap", display_name="🚜 Krymsk", battle_type=BattleType.GROUND),
    "664ccc91ada359263b247074f1f8b9f0f3e0efecf56f48df91fa27ec0": MapInfo(map_id="avg_kursk_villages_tankmap", display_name="🚜 Kursk Villages", battle_type=BattleType.GROUND),
    "d804902c93344e719ded21d07300f601dea3dc02f807701fa14d55b20": MapInfo(map_id="avg_lazzaro_italy_new_city_tankmap", display_name="🚜 Lazzaro Italy New City", battle_type=BattleType.GROUND),
    "a446af4d64b224acb949518554b9a87bd293342a6c5d2d6c71f042e48": MapInfo(map_id="avg_maginot_tankmap", display_name="🚜 Maginot", battle_type=BattleType.GROUND),
    "8e5910c071a1f38089c43df0e166c062816208c504e609300c8030000": MapInfo(map_id="avg_mozdok_tankmap", display_name="🚜 Mozdok", battle_type=BattleType.GROUND),
    "23f2e789acab6dd56faf9317a636a92d2e5ac93ddb96936af1b3476f8": MapInfo(map_id="avg_netherlands_tankmap", display_name="🚜 Netherlands", battle_type=BattleType.GROUND),
    "ed0244be9758cd41d3a59104e293443254a584ee08d610bc40b3d7a68": MapInfo(map_id="avg_normandy_tankmap", display_name="🚜 Normandy", battle_type=BattleType.GROUND),
    "3181278dcd6bbcde585999bcb1edd6dae593cb33a6ea0d5cf85570bc0": MapInfo(map_id="avg_northern_india_tankmap", display_name="🚜 Northern India", battle_type=BattleType.GROUND),
    "644e643caa32e4169a0eac32db327169298ad79ac7963b05b94b75568": MapInfo(map_id="avg_northern_valley_tankmap", display_name="🚜 Northern Valley", battle_type=BattleType.GROUND),
    "a4ae989d893a9a7575e2b64576892d165a1bfc5579cb330b6e07c94f8": MapInfo(map_id="avg_nuclear_incident_tankmap", display_name="🚜 Nuclear Incident", battle_type=BattleType.GROUND),
    "1c0a80ca5175c2168ea6144c5e1f1c6e341e656cca7f44f083f086fc8": MapInfo(map_id="avg_poland_snow_tankmap", display_name="🚜 Poland Snow", battle_type=BattleType.GROUND),
    "c3f51fc43cc8f9237b18e2b1e3e2c385872c8e113c00f601b69b79150": MapInfo(map_id="avg_poland_tankmap", display_name="🚜 Poland", battle_type=BattleType.GROUND),
    "28d313c21e96482d4e117024e05780ae01d8019a13bc818e039801f00": MapInfo(map_id="avg_port_novorossiysk_tankmap", display_name="🚜 Port Novorossiysk", battle_type=BattleType.GROUND),
    "718b8a86d6878b1d72929413a42ae597159a42eda7a24c5d2d900c388": MapInfo(map_id="avg_red_desert_tankmap", display_name="🚜 Red Desert", battle_type=BattleType.GROUND),
    "9765964f26af6b4eaa5e977e32fc79f86acbc766cd23934eaf836b060": MapInfo(map_id="avg_rheinland_tankmap", display_name="🚜 Rheinland", battle_type=BattleType.GROUND),
    "2410c8309231ae415cca2c942218a6390c623b00d6262c443928f0c88": MapInfo(map_id="avg_sector_montmedy_snow_tankmap", display_name="🚜 Sector Montmedy Snow", battle_type=BattleType.GROUND),
    "2650cc309820a041c4ca29942308a6390862338096261c44f028f0408": MapInfo(map_id="avg_sector_montmedy_tankmap", display_name="🚜 Sector Montmedy", battle_type=BattleType.GROUND),
    "9c1d0cc811f45ba87488f213b66d4c365c729cc93989932c00be81dd8": MapInfo(map_id="avg_snow_alps_tankmap", display_name="🚜 Snow Alps", battle_type=BattleType.GROUND),
    "38aa133c12cb6593dc6caddc58b2b32566421de433589645a92589c10": MapInfo(map_id="avg_soviet_range_tankmap", display_name="🚜 Soviet Range", battle_type=BattleType.GROUND),
    "c5e125e6c2db25764b8eb72f545c896903c38251a86010d870b0f1500": MapInfo(map_id="avg_soviet_suburban_snow_tankmap", display_name="🚜 Soviet Suburban Snow", battle_type=BattleType.GROUND),
    "f2d540c283b992726ad525ce2bb04b61b6572a394b78b339375328750": MapInfo(map_id="avg_soviet_suburban_tankmap", display_name="🚜 Soviet Suburban", battle_type=BattleType.GROUND),
    "238302c18a7ec2b10d627650eda7b137c65f99fee7e78f5c0ef01ec08": MapInfo(map_id="avg_stalingrad_factory_tankmap", display_name="🚜 Stalingrad Factory", battle_type=BattleType.GROUND),
    "43d003e603f031f053e257c07f80ff01fe03fc2ff81bf02fc04f903d0": MapInfo(map_id="avg_sweden_tankmap", display_name="🚜 Sweden", battle_type=BattleType.GROUND),
    "5d18f638f01869b273add64448098d152eacfa11e19d031a04bc03600": MapInfo(map_id="avg_syria_tankmap", display_name="🚜 Syria", battle_type=BattleType.GROUND),
    "b67f68fca0ea49939636166d0af84df25bc6378c6f89de93b9a1e7650": MapInfo(map_id="avg_training_ground_tankmap", display_name="🚜 Training Ground", battle_type=BattleType.GROUND),
    "ce0f3cbe75b7eaffd0f5b9e47f14be8a9d619f633f7af9b3f3c4ef8f8": MapInfo(map_id="avg_tunisia_desert_tankmap", display_name="🚜 Tunisia Desert", battle_type=BattleType.GROUND),
    "5b80c5c595d82c7858e30f849b04b68c270c3f0d725ce0cb820f08f78": MapInfo(map_id="avg_vietnam_hills_tankmap", display_name="🚜 Vietnam Hills", battle_type=BattleType.GROUND),
    "6672aa6764b258b2dac22f0a23506ab19956dc6da490c964330952548": MapInfo(map_id="avg_vlaanderen_tankmap", display_name="🚜 Vlaanderen", battle_type=BattleType.GROUND),
    "2b00cdc8f1627568d60b0a0669b6449c5c8db9c2f0ec645bc383a0488": MapInfo(map_id="avg_volokolamsk_tankmap", display_name="🚜 Volokolamsk", battle_type=BattleType.GROUND),
    "296a0eb524aac9d79bc6f605e88eb16d8ad91554a85a1084691d966c8": MapInfo(map_id="avg_western_europe_tankmap", display_name="🚜 Western Europe", battle_type=BattleType.GROUND),
}

AIR_IN_GROUND_MAPS = {
    "45265a9f99114921ce3b1d7036242e1ab4166096d29a4859c9b6684d8": MapInfo(map_id="avg_abandoned_factory_map", display_name="🚜 ✈️ Abandoned Factory", battle_type=BattleType.AIR_IN_GROUND),
    "222753668118542a95bb07372c74337e627844b5497d426accc8f5f60": MapInfo(map_id="avg_abandoned_town_map", display_name="🚜 ✈️ Abandoned Town", battle_type=BattleType.AIR_IN_GROUND),
    "a5921916134ca79a2f2efad96433c2262e9434eaa9e52ad4c5619d270": MapInfo(map_id="avg_alaska_town_map", display_name="🚜 ✈️ Alaska Town", battle_type=BattleType.AIR_IN_GROUND),
    "f017c066a59c43309367754ee2dda44d229f473ea48c6b3c6630cc618": MapInfo(map_id="avg_american_valley_map", display_name="🚜 ✈️ American Valley", battle_type=BattleType.AIR_IN_GROUND),
    "99cb316dd6f839397948d76bef2fc73fb24791bf35bcac6aa9a577ea8": MapInfo(map_id="avg_aral_sea_map", display_name="🚜 ✈️ Aral Sea", battle_type=BattleType.AIR_IN_GROUND),
    "5896cc19a2344b498d4109923ea36686a09a44d6c146ec45118a04620": MapInfo(map_id="avg_arctic_map", display_name="🚜 ✈️ Arctic", battle_type=BattleType.AIR_IN_GROUND),
    "eca3b286229cc0e983b15e48fcb0ed2ef4f527cf6f5ac75d5ad407a98": MapInfo(map_id="avg_ardennes_map", display_name="🚜 ✈️ Ardennes", battle_type=BattleType.AIR_IN_GROUND),
    "aca33307221c80ed23f14e49f412cd2c747534cd6f1ac74d5ad405a98": MapInfo(map_id="avg_ardennes_snow_map", display_name="🚜 ✈️ Ardennes Snow", battle_type=BattleType.AIR_IN_GROUND),
    "519282a620a260b86127812d88b5081a2835134e00600aa5950996280": MapInfo(map_id="avg_breslau_map", display_name="🚜 ✈️ Breslau", battle_type=BattleType.AIR_IN_GROUND),
    "de6866eb94f1cbe91704ef23cc29bdb3b82ad9b4f4b0e966c78986170": MapInfo(map_id="avg_container_port_map", display_name="🚜 ✈️ Container Port", battle_type=BattleType.AIR_IN_GROUND),
    "9e729ce995a131c2339413342346238b6240dd849c29840b2ca356a40": MapInfo(map_id="avg_eastern_europe_map", display_name="🚜 ✈️ Eastern Europe", battle_type=BattleType.AIR_IN_GROUND),
    "0bf52fc73cc330d161c2e3a5ce39886348c611c6264c37987f18bb080": MapInfo(map_id="avg_egypt_sinai_map", display_name="🚜 ✈️ Egypt Sinai", battle_type=BattleType.AIR_IN_GROUND),
    "e589cb0b479cdb81867689216258cc8e998d3b6a34cf4b83da27ae260": MapInfo(map_id="avg_european_fortress_map", display_name="🚜 ✈️ European Fortress", battle_type=BattleType.AIR_IN_GROUND),
    "254821287158c4b827215a631412c23700ec974c52366654c4cc958d0": MapInfo(map_id="avg_finland_map", display_name="🚜 ✈️ Finland", battle_type=BattleType.AIR_IN_GROUND),
    "00fe13fc12f86cf09de123d227a46f489e92bd227a68f05be017c05f8": MapInfo(map_id="avg_football_field_map", display_name="🚜 ✈️ Football Field", battle_type=BattleType.AIR_IN_GROUND),
    "6cc7b183e6678d2e1bda26d4cde8b1c9aab14e25bf0b263a5e7832730": MapInfo(map_id="avg_fulda_map", display_name="🚜 ✈️ Fulda", battle_type=BattleType.AIR_IN_GROUND),
    "90f503d21b90eb62f293e6206490f1d0e290e054a691c5a30b2325518": MapInfo(map_id="avg_future_city_map", display_name="🚜 ✈️ Future City", battle_type=BattleType.AIR_IN_GROUND),
    "8e12cb1c60b0a3630ece3d85b30c47300e001c0048c471807200c0008": MapInfo(map_id="avg_greece_map", display_name="🚜 ✈️ Greece", battle_type=BattleType.AIR_IN_GROUND),
    "f0edd3f260b07331e382f19b31ec59c49941bf2495812ee0aa9018490": MapInfo(map_id="avg_guadalcanal_map", display_name="🚜 ✈️ Guadalcanal", battle_type=BattleType.AIR_IN_GROUND),
    "42bd127c8731a2529435c137224dc7e3958e947118dcbe39292f405b8": MapInfo(map_id="avg_hurtgen_map", display_name="🚜 ✈️ Hurtgen", battle_type=BattleType.AIR_IN_GROUND),
    "705d547b56ee907451e2b380a3018e0b1810001100020000000000000": MapInfo(map_id="avg_iberian_castle_map", display_name="🚜 ✈️ Iberian Castle", battle_type=BattleType.AIR_IN_GROUND),
    "60e588f229e24b8857041c4afc0df819f813f42b984f738ec65689ad8": MapInfo(map_id="avg_israel_map", display_name="🚜 ✈️ Israel", battle_type=BattleType.AIR_IN_GROUND),
    "11beb07eb545ca71e0e3c446d483948618036104c461a3c30dc61a9c0": MapInfo(map_id="avg_japan_map", display_name="🚜 ✈️ Japan", battle_type=BattleType.AIR_IN_GROUND),
    "1c70bae0f1c8e399cf03cf07192e383e70f961fa83f806790cf63d880": MapInfo(map_id="avg_karelia_forest_a_map", display_name="🚜 ✈️ Karelia Forest A", battle_type=BattleType.AIR_IN_GROUND),
    "66cc4367c677b5c3f91b7b336426e6e253e03190b1909029ae130bb98": MapInfo(map_id="avg_karpaty_passage_map", display_name="🚜 ✈️ Karpaty Passage", battle_type=BattleType.AIR_IN_GROUND),
    "4c8a352858b0d0773078d9a19367a065409686cc1d182e308e459c928": MapInfo(map_id="avg_korea_lake_map", display_name="🚜 ✈️ Korea Lake", battle_type=BattleType.AIR_IN_GROUND),
    "60e9439887118c631846020408039015205a274020046000402884400": MapInfo(map_id="avg_lazzaro_italy_map", display_name="🚜 ✈️ Lazzaro Italy", battle_type=BattleType.AIR_IN_GROUND),
    "0cb0086418d022a04e08d915100b8217b088481030256043009709220": MapInfo(map_id="avg_maginot_map", display_name="🚜 ✈️ Maginot", battle_type=BattleType.AIR_IN_GROUND),
    "922596622a659609305571ee871a9275aa22a5984a34386c64c8b1f50": MapInfo(map_id="avg_netherlands_map", display_name="🚜 ✈️ Netherlands", battle_type=BattleType.AIR_IN_GROUND),
    "eba21650881bd055e213c2238c9b507548ea80c492c9249c43198e368": MapInfo(map_id="avg_northern_india_map", display_name="🚜 ✈️ Northern India", battle_type=BattleType.AIR_IN_GROUND),
    "737dbde15fc0f80ae035efba91d6469a694b43a72b832b452d9873b08": MapInfo(map_id="avg_northern_valley_map", display_name="🚜 ✈️ Northern Valley", battle_type=BattleType.AIR_IN_GROUND),
    "ed0090707ae1f0c3c79aaf4bc78f1e0d1e9e1c12382c301c200e40148": MapInfo(map_id="avg_poland_map", display_name="🚜 ✈️ Poland", battle_type=BattleType.AIR_IN_GROUND),
    "ed0091707ae1f1c3c79aaf4bc78f1e0d1e9e1c12382c301c200e40148": MapInfo(map_id="avg_poland_snow_map", display_name="🚜 ✈️ Poland Snow", battle_type=BattleType.AIR_IN_GROUND),
    "4bba8f6d0fa62b44839b99f18cb3ca278207000c30002000000000000": MapInfo(map_id="avg_port_novorossiysk_map", display_name="🚜 ✈️ Port Novorossiysk", battle_type=BattleType.AIR_IN_GROUND),
    "489b331c5a3855d96ab8d331ea29cf56aa0f24162e6c18ea73136a648": MapInfo(map_id="avg_red_desert_map", display_name="🚜 ✈️ Red Desert", battle_type=BattleType.AIR_IN_GROUND),
    "b033e4637036e0c9c011e0b3f373c4f58de313e287c70fc65f823f060": MapInfo(map_id="avg_rheinland_map", display_name="🚜 ✈️ Rheinland", battle_type=BattleType.AIR_IN_GROUND),
    "cd891182b125322a3c5d96bd1655033b4c77646e50bad09e981c311b8": MapInfo(map_id="avg_sector_montmedy_map", display_name="🚜 ✈️ Sector Montmedy", battle_type=BattleType.AIR_IN_GROUND),
    "cd891082b125322a3c5d96bd165503bb4d77606e509ad09e901d311b8": MapInfo(map_id="avg_sector_montmedy_snow_map", display_name="🚜 ✈️ Sector Montmedy Snow", battle_type=BattleType.AIR_IN_GROUND),
    "6272d5e476469b030d4cd13302e473a1ee86ce4699856d9ba90aea1b0": MapInfo(map_id="avg_snow_alps_map", display_name="🚜 ✈️ Snow Alps", battle_type=BattleType.AIR_IN_GROUND),
    "21206b24331c27928a6cd07b5430a64e2b8568524dce692ac2a1bc668": MapInfo(map_id="avg_soviet_range_map", display_name="🚜 ✈️ Soviet Range", battle_type=BattleType.AIR_IN_GROUND),
    "71216243221347048a49a5329c3515c8b16148c55d894d689ea11c440": MapInfo(map_id="avg_soviet_suburban_map", display_name="🚜 ✈️ Soviet Suburban", battle_type=BattleType.AIR_IN_GROUND),
    "33235d44b39b67128a2dc57b9835149a3b456cf15d8c49aaaac17b468": MapInfo(map_id="avg_soviet_suburban_snow_map", display_name="🚜 ✈️ Soviet Suburban Snow", battle_type=BattleType.AIR_IN_GROUND),
    "0136026e139c1e7498f15bd097a12f4a3e2e7c01fa6ff9afe317c43f8": MapInfo(map_id="avg_sweden_map", display_name="🚜 ✈️ Sweden", battle_type=BattleType.AIR_IN_GROUND),
    "d2c9f123aa2cb0d1638867104e625c79d4cf135a29d4b7b1b2e465920": MapInfo(map_id="avg_syria_map", display_name="🚜 ✈️ Syria", battle_type=BattleType.AIR_IN_GROUND),
    "e1c6837c47d00f807e037c02f08de023e087c08fc10f801f827f80d70": MapInfo(map_id="avg_tunisia_desert_map", display_name="🚜 ✈️ Tunisia Desert", battle_type=BattleType.AIR_IN_GROUND),
    "0cbe19fc5f782ef46fe93f9cbf3dfe39fc7270fe46f88c70186034000": MapInfo(map_id="avg_vietnam_hills_map", display_name="🚜 ✈️ Vietnam Hills", battle_type=BattleType.AIR_IN_GROUND),
    "4038005401a802c005800bc012802980c3811b826720de600ec029820": MapInfo(map_id="avg_vlaanderen_map", display_name="🚜 ✈️ Vlaanderen", battle_type=BattleType.AIR_IN_GROUND),
    "e651c5230296184e989d63ad435a96d52d6658c4d49c4d541a4b38660": MapInfo(map_id="avg_volokolamsk_map", display_name="🚜 ✈️ Volokolamsk", battle_type=BattleType.AIR_IN_GROUND),
    "8517855987e6a15916995642d8d313a7313c72596118be39306c95198": MapInfo(map_id="avg_western_europe_map", display_name="🚜 ✈️ Western Europe", battle_type=BattleType.AIR_IN_GROUND),
}

NAVAL_MAPS = {
    "fc09c942030a11681e401f803f8c6308ce559ca7f94bf077f16fe25f0": MapInfo(map_id="avn_africa_gulf_tankmap", display_name="⛵ Africa Gulf", battle_type=BattleType.NAVAL),
    "02d30de755f6a9f973000000000000037e027e05f0000000144804540": MapInfo(map_id="avn_aleutian_islands_tankmap", display_name="⛵ Aleutian Islands", battle_type=BattleType.NAVAL),
    "0d9619ac33884298951128f054b1b53126a16b51b4c1d380c04d20ce0": MapInfo(map_id="avn_alps_fjord_tankmap", display_name="⛵ Alps Fjord", battle_type=BattleType.NAVAL),
    "394d32326868849e2a6eb459ca4c28a9499890c91866983c42d222738": MapInfo(map_id="avn_arabian_north_coast_tankmap", display_name="⛵ Arabian North Coast", battle_type=BattleType.NAVAL),
    "d86532f2a447088c137830f03349a301ea61de625480a832906416398": MapInfo(map_id="avn_bering_sea_tankmap", display_name="⛵ Bering Sea", battle_type=BattleType.NAVAL),
    "10c03180d217212c4d086212d54c865528a158709ca21e2a39a473ad8": MapInfo(map_id="avn_blacksea_port_tankmap", display_name="⛵ Blacksea Port", battle_type=BattleType.NAVAL),
    "006008c0158097021981d1832606761cd83aa84ab007e0196011c0000": MapInfo(map_id="avn_coral_islands_tankmap", display_name="⛵ Coral Islands", battle_type=BattleType.NAVAL),
    "f1a7f24ed11d865f4d9f126e2cd63bfa9b89cf16965d889a001d42138": MapInfo(map_id="avn_england_shore_tankmap", display_name="⛵ England Shore", battle_type=BattleType.NAVAL),
    "7000e413120046020b085f10ce033e823901e003000e889938007c048": MapInfo(map_id="avn_fiji_tankmap", display_name="⛵ Fiji", battle_type=BattleType.NAVAL),
    "086c198ea63c972a2cc13ac3af87870f0e1e1c7838e03020b44804540": MapInfo(map_id="avn_finland_islands_tankmap", display_name="⛵ Finland Islands", battle_type=BattleType.NAVAL),
    "01fe0ffc1df819f031e075c0ab85df027e06fc05f803e017b04f007c0": MapInfo(map_id="avn_franz_josef_land_tankmap", display_name="⛵ Franz Josef Land", battle_type=BattleType.NAVAL),
    "ff801f05e71ace1ec43d81cf332ec23d88dd0baf1d1e351c279837140": MapInfo(map_id="avn_fuego_islands_tankmap", display_name="⛵ Fuego Islands", battle_type=BattleType.NAVAL),
    "2c40490c34f8e860cb013b053602bc308822180410190006460c4c188": MapInfo(map_id="avn_ice_port_tankmap", display_name="⛵ Ice Port", battle_type=BattleType.NAVAL),
    "af6b985b708a184839a17b02cc051e049e12fe30f879f6bbfb7dbb7c0": MapInfo(map_id="avn_ireland_bay_tankmap", display_name="⛵ Ireland Bay", battle_type=BattleType.NAVAL),
    "395073815512b899e335410d580cb8117046f409b8307070e1e5c46b8": MapInfo(map_id="avn_japan_tankmap", display_name="⛵ Japan", battle_type=BattleType.NAVAL),
    "d6f1edc0eb01c6034c855120d8c021004100968114020204461650940": MapInfo(map_id="avn_mediterranean_port_tankmap", display_name="⛵ Mediterranean Port", battle_type=BattleType.NAVAL),
    "b272247748e7254e7238c02ea83861c821815068b95130a420c4a3100": MapInfo(map_id="avn_new_zealand_tankmap", display_name="⛵ New Zealand", battle_type=BattleType.NAVAL),
    "c842a405a1058e40ce434e004c438e573f346b037003e001c000e2808": MapInfo(map_id="avn_northwestern_islands_tankmap", display_name="⛵ Northwestern Islands", battle_type=BattleType.NAVAL),
    "c283ccc79ecd3999e32b36f57ce6bfca7f15ef251f63984d587451608": MapInfo(map_id="avn_north_sea_tankmap", display_name="⛵ North Sea", battle_type=BattleType.NAVAL),
    "c5d86364fcccf113c26c8cb98a62a9d32738d371a7826138a2b208c40": MapInfo(map_id="avn_norway_islands_tankmap", display_name="⛵ Norway Islands", battle_type=BattleType.NAVAL),
    "00fe017c0cf819f03be09bc08f839f053e01fc05f817f02fe01f807e8": MapInfo(map_id="avn_peleliu_tankmap", display_name="⛵ Peleliu", battle_type=BattleType.NAVAL),
    "b7454e51348d1b105c055813381b61b20335021c86700e280ce019c80": MapInfo(map_id="avn_phang_nga_bay_islands_tankmap", display_name="⛵ Phang Nga Bay Islands", battle_type=BattleType.NAVAL),
    "442b6865942f6841d980c7818f511c80179097262e4e5c11dc3b9d750": MapInfo(map_id="avn_san_francisco_tankmap", display_name="⛵ San Francisco", battle_type=BattleType.NAVAL),
    "8bfecb7f9efc5ffb03e667c0b5817303260f841f383e603e007800780": MapInfo(map_id="avn_south_africa_tankmap", display_name="⛵ South Africa", battle_type=BattleType.NAVAL),
    "9936b9c0bca5c997a42da61c84fe5272b8caccda44998e191c241ac40": MapInfo(map_id="avn_sunken_city_tankmap", display_name="⛵ Sunken City", battle_type=BattleType.NAVAL),
    "b66dad0d52dc6b1b293a775c35552068d75b8a4cae4a459967449eaa0": MapInfo(map_id="avn_volcanic_island_tankmap", display_name="⛵ Volcanic Island", battle_type=BattleType.NAVAL),
}

AIR_IN_NAVAL_MAPS = {
    "062e003c28783c507c20dc41bc825c80dc019c4038407461620911228": MapInfo(map_id="avn_africa_gulf_map", display_name="⛵ ✈️ Africa Gulf", battle_type=BattleType.AIR_IN_NAVAL),
    "d087302ee09e803c383871e00cc07b0c7071f040b8a17832c066be290": MapInfo(map_id="avn_aleutian_islands_map", display_name="⛵ ✈️ Aleutian Islands", battle_type=BattleType.AIR_IN_NAVAL),
    "2ae2c7c416018a43150210262029401080548024006e0880036005200": MapInfo(map_id="avn_alps_fjord_map", display_name="⛵ ✈️ Alps Fjord", battle_type=BattleType.AIR_IN_NAVAL),
    "0f081d48b8cbcc37ac6870a1cbb64b98c9c988ee09db93e7209d40b30": MapInfo(map_id="avn_arabian_north_coast_map", display_name="⛵ ✈️ Arabian North Coast", battle_type=BattleType.AIR_IN_NAVAL),
    "d80b3036e16e623aa034642364c6098d19125630d442e80e100a36790": MapInfo(map_id="avn_bering_sea_map", display_name="⛵ ✈️ Bering Sea", battle_type=BattleType.AIR_IN_NAVAL),
    "15617b126108e40a6b05cb07a50e2a9d95daab2338825489b5b550e30": MapInfo(map_id="avn_blacksea_port_map", display_name="⛵ ✈️ Blacksea Port", battle_type=BattleType.AIR_IN_NAVAL),
    "14526a43688a6494ad2c1918de1038246521fa64f46548a10c06151d0": MapInfo(map_id="avn_coral_islands_map", display_name="⛵ ✈️ Coral Islands", battle_type=BattleType.AIR_IN_NAVAL),
    "99a823cb6395bf2eff09bc10f8a7e09f20a7289f255e0dbc2a7835788": MapInfo(map_id="avn_england_shore_map", display_name="⛵ ✈️ England Shore", battle_type=BattleType.AIR_IN_NAVAL),
    "80a48828207101f045e807d04f307c62e0c7e11fc03f807cb07020500": MapInfo(map_id="avn_fiji_map", display_name="⛵ ✈️ Fiji", battle_type=BattleType.AIR_IN_NAVAL),
    "15b249c19946960c5b189a765432984b68b2504090813812c06492218": MapInfo(map_id="avn_finland_islands_map", display_name="⛵ ✈️ Finland Islands", battle_type=BattleType.AIR_IN_NAVAL),
    "c3a746954a4d4675a33333070d695cb6f035f061b0817032c06496798": MapInfo(map_id="avn_franz_josef_land_map", display_name="⛵ ✈️ Franz Josef Land", battle_type=BattleType.AIR_IN_NAVAL),
    "634906ab5a2b1a3038f993fbe697e57bc879c9e29a1d9438ca53b9830": MapInfo(map_id="avn_fuego_islands_map", display_name="⛵ ✈️ Fuego Islands", battle_type=BattleType.AIR_IN_NAVAL),
    "13520d241288339096614c82110091300e2038146018200022094c368": MapInfo(map_id="avn_ice_port_map", display_name="⛵ ✈️ Ice Port", battle_type=BattleType.AIR_IN_NAVAL),
    "cc4c8c9165e186971964b2d1a356071d4830d1609a3198e04a1290838": MapInfo(map_id="avn_ireland_bay_map", display_name="⛵ ✈️ Ireland Bay", battle_type=BattleType.AIR_IN_NAVAL),
    "f16530c864e099c0330087231c2298d2b990f150b091f83a406416698": MapInfo(map_id="avn_japan_map", display_name="⛵ ✈️ Japan", battle_type=BattleType.AIR_IN_NAVAL),
    "a66c552a1ac666e4cdc99629ac4df8a96150d1b096b12c92d44492590": MapInfo(map_id="avn_mediterranean_port_map", display_name="⛵ ✈️ Mediterranean Port", battle_type=BattleType.AIR_IN_NAVAL),
    "c49269441e986411e169808e20b9a0cb21844108987110e0214090100": MapInfo(map_id="avn_new_zealand_map", display_name="⛵ ✈️ New Zealand", battle_type=BattleType.AIR_IN_NAVAL),
    "266209cc960f59458999953105c689c4b3459e242c4f5048909151108": MapInfo(map_id="avn_northwestern_islands_map", display_name="⛵ ✈️ Northwestern Islands", battle_type=BattleType.AIR_IN_NAVAL),
    "20c0008001a00170c2e1814601ac0fd90f2d27496c80d6202f104d718": MapInfo(map_id="avn_north_sea_map", display_name="⛵ ✈️ North Sea", battle_type=BattleType.AIR_IN_NAVAL),
    "b672ed5cf4c9a9636964a4521906720524c963124e0abc4549b3b1ad0": MapInfo(map_id="avn_norway_islands_map", display_name="⛵ ✈️ Norway Islands", battle_type=BattleType.AIR_IN_NAVAL),
    "d87d313ae077087c38f8f9e03148fa01a8725c6038a07821c047964d8": MapInfo(map_id="avn_peleliu_map", display_name="⛵ ✈️ Peleliu", battle_type=BattleType.AIR_IN_NAVAL),
    "18f4a169c4e29b947c04d30bae165e20946128b7499a735aa6a202cc0": MapInfo(map_id="avn_phang_nga_bay_islands_map", display_name="⛵ ✈️ Phang Nga Bay Islands", battle_type=BattleType.AIR_IN_NAVAL),
    "3253a086cd0d4a5996491371caf098c05981fa0372046808f6315d728": MapInfo(map_id="avn_san_francisco_map", display_name="⛵ ✈️ San Francisco", battle_type=BattleType.AIR_IN_NAVAL),
    "5e3f393c18f93af4d5ce2d13fc61f800f853f450b811f832446616698": MapInfo(map_id="avn_south_africa_map", display_name="⛵ ✈️ South Africa", battle_type=BattleType.AIR_IN_NAVAL),
    "a72a23a917782ec29d451b0927b08ee3198c820000000000000000000": MapInfo(map_id="avn_sunken_city_map", display_name="⛵ ✈️ Sunken City", battle_type=BattleType.AIR_IN_NAVAL),
    "c12854545b88979a0b641a597680ef40d45e889914a70913328413340": MapInfo(map_id="avn_volcanic_island_map", display_name="⛵ ✈️ Volcanic Island", battle_type=BattleType.AIR_IN_NAVAL),
}

UNKNOWN_MAPS = {
    "429e357e19ff337d8d7a99d6cfac9f293f251e726cd4fe69bcfbfac30": MapInfo(map_id="avg_africa_canyon_map", display_name="Africa Canyon", battle_type=BattleType.UNKNOWN),
    "c4d289c912f4146818f95160a5714c819b0d8f2a5c33b826732a33188": MapInfo(map_id="avg_africa_seashore_map", display_name="Africa Seashore", battle_type=BattleType.UNKNOWN),
    "418283858e0b9831616282c6118a330e463d853a0be1d9c3b786370e0": MapInfo(map_id="avg_alps_map", display_name="Alps", battle_type=BattleType.UNKNOWN),
    "7bc2f64de29e441d710ad20726134d6a8aed04de1fbd16da07985e390": MapInfo(map_id="avg_asia_4roads_map", display_name="Asia 4roads", battle_type=BattleType.UNKNOWN),
    "fd07e197e53f9927003e607da165e2e9c1fa17e40f7b1f7b0fe68fe60": MapInfo(map_id="avg_canyon_snow_map", display_name="Canyon Snow", battle_type=BattleType.UNKNOWN),
    "266a68dcacfc31f275ef23af33a54d71c86330d2e93196f26fc4cd1d8": MapInfo(map_id="avg_ireland_map", display_name="Ireland", battle_type=BattleType.UNKNOWN),
    "836e4ee9c5eb4c9257b6c4d7672e8f4cdcb55da6cb6d625424f46b358": MapInfo(map_id="avg_mediterranean_map", display_name="Mediterranean", battle_type=BattleType.UNKNOWN),
    "d86d3cf65dcd977e497586734ccb6ec42f593fa97f84fcc5332e2cca0": MapInfo(map_id="avg_norway_fjords_map", display_name="Norway Fjords", battle_type=BattleType.UNKNOWN),
    "8caaa75b64464904c508cab04c5850ab42ce88da02a94db18f62bac60": MapInfo(map_id="avg_norway_green_map", display_name="Norway Green", battle_type=BattleType.UNKNOWN),
    "1b660cc9cb6b1861448aca31a459c888308881f203c943a28e661ece0": MapInfo(map_id="avg_norway_plain_map", display_name="Norway Plain", battle_type=BattleType.UNKNOWN),
    "7238e4fef44cad3329e5554a32992f2a822f346a3e30d5768e9588a60": MapInfo(map_id="avg_phiphi_crater_map", display_name="Phiphi Crater", battle_type=BattleType.UNKNOWN),
    "0ff0a9acb38ad71553e665c253952f48bc89a416d9165686e9a7c3660": MapInfo(map_id="avg_phiphi_crater_rocks_map", display_name="Phiphi Crater Rocks", battle_type=BattleType.UNKNOWN),
    "82ed30882b816b265e3474a9ed13a04b2736af6f44db4c6e47d20ae60": MapInfo(map_id="avg_rice_terraces_map", display_name="Rice Terraces", battle_type=BattleType.UNKNOWN),
    "12526b82e706fa89fd1dda3dbc7778ce719def1e6d6b19c66ace8d9d0": MapInfo(map_id="avg_snow_rocks_map", display_name="Snow Rocks", battle_type=BattleType.UNKNOWN),
    "01b082f005e00fe06fe05bc8e7894f003f00fd107a4872012000c0018": MapInfo(map_id="avg_tabletop_mountain_map", display_name="Tabletop Mountain", battle_type=BattleType.UNKNOWN),
    "64424aa4d518c87c7253647122498dcd308af08c219d4e2e024e46560": MapInfo(map_id="avg_zhang_park_map", display_name="Zhang Park", battle_type=BattleType.UNKNOWN),
    "32064430400d42936546f08cb4ac7824b6ca7355d50ca5162a6404ab0": MapInfo(map_id="berlin", display_name="Berlin", battle_type=BattleType.UNKNOWN),
    "381ca23b9c7f7aff7dc45f997e20fc27f28f22b0954102c2118820900": MapInfo(map_id="britain", display_name="Britain", battle_type=BattleType.UNKNOWN),
    "1946342cf069a1510fb53e49d606ea4f9f067947f0afa017630cc12e8": MapInfo(map_id="bulge", display_name="Bulge", battle_type=BattleType.UNKNOWN),
    "6544bb0c1874404886c11f0816006a05dc1ec1a98e5ee323c599fa4e0": MapInfo(map_id="caribbean_islands", display_name="Caribbean Islands", battle_type=BattleType.UNKNOWN),
    "e201900200033009603fc047818e02e001c00001a801c009ca07c9058": MapInfo(map_id="dover_strait", display_name="Dover Strait", battle_type=BattleType.UNKNOWN),
    "ba95d1933626689938b1c48638943af663b8e9b1d375a5a743431ea68": MapInfo(map_id="firing_range_tankmap", display_name="Firing Range Tankmap", battle_type=BattleType.UNKNOWN),
    "f0e9d3fa61b071f0e0e1e15b329c593cf279bc7d90bd21dee06ec25e8": MapInfo(map_id="guadalcanal", display_name="Guadalcanal", battle_type=BattleType.UNKNOWN),
    "407d80fa01f421f8c3e00f803f027507df17483ea07e817902e31e630": MapInfo(map_id="guam", display_name="Guam", battle_type=BattleType.UNKNOWN),
    "0eb99dd30e241e083c1338a17f617fc27ec47dc1f38ce383860706af8": MapInfo(map_id="honolulu", display_name="Honolulu", battle_type=BattleType.UNKNOWN),
    "272b5615b421ae56ac33927664cdc3c3038e247398ddba297925506f8": MapInfo(map_id="hurtgen", display_name="Hurtgen", battle_type=BattleType.UNKNOWN),
    "4d085e047a18d032c3bc29a43848f231b20548b891ec70f820f040ec8": MapInfo(map_id="iwo_jima", display_name="Iwo Jima", battle_type=BattleType.UNKNOWN),
    "1401c8339a67189e19a712236c46709d103c603800370133ce7c3cd00": MapInfo(map_id="khalkhin_gol", display_name="Khalkhin Gol", battle_type=BattleType.UNKNOWN),
    "4d342558db6b174da5668b59ba331cda57a4ad04635ba16b14ac391d0": MapInfo(map_id="korea", display_name="Korea", battle_type=BattleType.UNKNOWN),
    "ad225f05b283678c4ed48cf1336264451b1126922d464c1b9e11b8ad0": MapInfo(map_id="korsun", display_name="Korsun", battle_type=BattleType.UNKNOWN),
    "03ca8ff20fc21f863f853d438d051c810de241f804c6180e2216084b0": MapInfo(map_id="krymsk", display_name="Krymsk", battle_type=BattleType.UNKNOWN),
    "cb03ad2268949d461d212ccb56c6c9c9b2c75794ee61adc797261c648": MapInfo(map_id="kursk", display_name="Kursk", battle_type=BattleType.UNKNOWN),
    "a0f181e426907104f100f9007004b8a1f981fbc0e3c686e00c7008580": MapInfo(map_id="malta", display_name="Malta", battle_type=BattleType.UNKNOWN),
    "02fe01fc03f80ff00f901fc07fc07f00fc01f8037806f00f601880270": MapInfo(map_id="midway", display_name="Midway", battle_type=BattleType.UNKNOWN),
    "0cf35decfba47e1cd5156bf2bad4f4ecf5d5cfad9f58d5642076a2eb0": MapInfo(map_id="moscow", display_name="Moscow", battle_type=BattleType.UNKNOWN),
    "e9bedafdf75b8b75f0fcfe41df8fef07bd17d6afd297e5235e4b849e8": MapInfo(map_id="mozdok", display_name="Mozdok", battle_type=BattleType.UNKNOWN),
    "c9fe7aac6bd98bf4f0eb1e78c3f033980cf8c4b054403aa3b64b249e8": MapInfo(map_id="mozdok_winter", display_name="Mozdok Winter", battle_type=BattleType.UNKNOWN),
    "8644869b06261cec5188887209e312cb6982c906062d0c5a18f9330a0": MapInfo(map_id="norway", display_name="Norway", battle_type=BattleType.UNKNOWN),
    "65d062a4836b24d34bc64ed71c4c78b4b907108ba04419b039a2ddf08": MapInfo(map_id="peleliu", display_name="Peleliu", battle_type=BattleType.UNKNOWN),
    "a404140388058205842b80930017042608151a410b611cc9152910ca0": MapInfo(map_id="port_moresby", display_name="Port Moresby", battle_type=BattleType.UNKNOWN),
    "006c10ca164618c4256c615c42284b304c6132c08e803d813f821f000": MapInfo(map_id="ruhr", display_name="Ruhr", battle_type=BattleType.UNKNOWN),
    "65d062a4836b24d34b465cb7344dd8b3b903108ba04419b039e2ddd08": MapInfo(map_id="saipan", display_name="Saipan", battle_type=BattleType.UNKNOWN),
    "60ffa2ff17f44bd56faaef339eebbf295f917f53facbfe78e5ee8abb0": MapInfo(map_id="sicily", display_name="Sicily", battle_type=BattleType.UNKNOWN),
    "3f0cb61d683fa1ae88d955b4c36a9f873d5de09b953781ff06f87fc88": MapInfo(map_id="spain", display_name="Spain", battle_type=BattleType.UNKNOWN),
    "82f886e1c7819a21fc01f877e1b78a3f503c227040dc11d803c800d80": MapInfo(map_id="stalingrad", display_name="Stalingrad", battle_type=BattleType.UNKNOWN),
    "82f886e1c7819b21fc01f873e0b7c03f403c227040fd31d803c900d80": MapInfo(map_id="stalingrad_w", display_name="Stalingrad W", battle_type=BattleType.UNKNOWN),
    "0000000000000f002600c60098007005800b0016002c0000000000000": MapInfo(map_id="unknownmap", display_name="Unknownmap", battle_type=BattleType.UNKNOWN),
    "071206060a9c17282f203ca079c0e368f879ed75c35b87b710c6270a8": MapInfo(map_id="wake_island", display_name="Wake Island", battle_type=BattleType.UNKNOWN),
    "50c7202e419ca1335064834a8d531ae135d05d4662890a24859324540": MapInfo(map_id="water", display_name="Water", battle_type=BattleType.UNKNOWN),
    "38e9c0628d9e022c89d4e321d21da16f187f7affefd9ecf8ccf9bcfe0": MapInfo(map_id="zhengzhou", display_name="Zhengzhou", battle_type=BattleType.UNKNOWN),
    "0000048036008f002604e6061802600580034016800c0020001000000": MapInfo(map_id="no_map", display_name="No Map", battle_type=BattleType.UNKNOWN),
}

ALL_MAPS = {
    **AIR_MAPS,
    **GROUND_MAPS,
    **AIR_IN_GROUND_MAPS,
    **NAVAL_MAPS,
    **AIR_IN_NAVAL_MAPS,
    **UNKNOWN_MAPS,
}

UNKNOWN_MAP_INFO = MapInfo(map_id="unknown", display_name="Unknown Map", battle_type=BattleType.UNKNOWN)


def _append_missing_hash(
    dhash: str,
    best_distance: Optional[int],
    closest_hash: Optional[str],
    closest_map_id: Optional[str],
    context: Optional[str],
) -> None:
    import json
    from datetime import datetime, timezone
    from pathlib import Path

    try:
        log_path = Path(__file__).resolve().parent / "data" / "missing_map_hashes.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "time": datetime.now(timezone.utc).isoformat(),
            "hash": dhash,
            "length": len(dhash),
            "best_distance": best_distance,
            "closest_hash": closest_hash,
            "closest_map_id": closest_map_id,
            "context": context,
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except Exception:
        # Avoid breaking capture flow if logging fails
        pass

def lookup_map_info(dhash: str, context: Optional[str] = None) -> MapInfo:
    """
    Look up map metadata from dhash.
    Returns MapInfo or a fallback if not found.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Try exact match first
    if dhash in ALL_MAPS:
        logger.debug(f"Exact hash match: {dhash}")
        return ALL_MAPS[dhash]

    # Try to find closest match (hamming distance)
    # This helps with slight image variations
    tolerance = 42
    best_match = None
    best_distance = float('inf')
    closest_distance = float('inf')
    closest_hash = None
    closest_map_id = None
    closest_info = None

    for known_hash, info in ALL_MAPS.items():
        distance = _hamming_distance(dhash, known_hash)
        if distance < closest_distance:
            closest_distance = distance
            closest_hash = known_hash
            closest_map_id = info.map_id
            closest_info = info

    if closest_info is not None:
        if closest_distance <= tolerance:
            best_distance = closest_distance
            best_match = closest_info

    if best_match:
        logger.info(
            f"Fuzzy hash match: {best_match.display_name} (distance: {best_distance})")
    else:
        logger.warning(
            f"No hash match found for: {dhash} ({len(dhash)} chars)")
        closest_value = None if closest_distance == float('inf') else int(closest_distance)
        _append_missing_hash(dhash, closest_value, closest_hash, closest_map_id, context)
        # Log a sample known hash for comparison
        sample_hash = list(ALL_MAPS.keys())[0]
        logger.warning(
            f"Sample known hash: {sample_hash} ({len(sample_hash)} chars)")

    return best_match or UNKNOWN_MAP_INFO


def lookup_map_name(dhash: str, context: Optional[str] = None) -> str:
    """
    Look up map name from dhash.
    Returns the display name or 'Unknown Map' if not found.
    """
    return lookup_map_info(dhash, context=context).display_name


def _hamming_distance(hash1: str, hash2: str) -> int:
    """Calculate hamming distance between two hex hashes."""
    # Handle length mismatch by padding shorter one
    if len(hash1) != len(hash2):
        max_len = max(len(hash1), len(hash2))
        hash1 = hash1.ljust(max_len, '0')
        hash2 = hash2.ljust(max_len, '0')

    distance = 0
    for c1, c2 in zip(hash1, hash2):
        try:
            # Convert hex chars to int and XOR
            b1 = int(c1, 16)
            b2 = int(c2, 16)
            xor = b1 ^ b2
            # Count bits
            distance += bin(xor).count('1')
        except ValueError:
            distance += 4  # Max difference for invalid chars

    return distance
