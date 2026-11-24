import CoreBluetooth
import Foundation

let service = CBUUID(string: "823ef401-1d82-41f6-b689-68aedcbb1960")
let sample = CBUUID(string: "823ef402-1d82-41f6-b689-68aedcbb1960")
final class Check: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var target: CBPeripheral?
    private var retryPending = false
    func retry(_ manager: CBCentralManager) {
        if let peripheral = target { manager.cancelPeripheralConnection(peripheral) }
        target = nil
        guard !retryPending else { return }
        retryPending = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
            self?.retryPending = false
            if manager.state == .poweredOn { manager.scanForPeripherals(withServices: [service]) }
        }
    }
    func centralManager(_ manager: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        if peripheral == target { retry(manager) }
    }
    func centralManagerDidUpdateState(_ manager: CBCentralManager) {
        if manager.state == .poweredOn { manager.scanForPeripherals(withServices: [service]) }
        else if manager.state != .unknown && manager.state != .resetting { print("Bluetooth state:", manager.state.rawValue); fflush(stdout) }
    }
    func centralManager(_ manager: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi RSSI: NSNumber) {
        let name = advertisementData[CBAdvertisementDataLocalNameKey] as? String ?? peripheral.name ?? ""
        guard name == "SmartDumbbell" else { return }
        target = peripheral
        manager.stopScan()
        manager.connect(peripheral)
    }
    func centralManager(_ manager: CBCentralManager, didConnect peripheral: CBPeripheral) {
        peripheral.delegate = self
        peripheral.discoverServices([service])
    }
    func centralManager(_ manager: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        print("GATT connection failed:", error?.localizedDescription ?? "unknown error")
        retry(manager)
    }
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let match = peripheral.services?.first(where: { $0.uuid == service }) else {
            print("Expected service could not be read:", error?.localizedDescription ?? "missing service")
            retry(central); return
        }
        peripheral.discoverCharacteristics([sample], for: match)
    }
    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard let match = service.characteristics?.first(where: { $0.uuid == sample }) else {
            print("Expected characteristic could not be read:", error?.localizedDescription ?? "missing characteristic")
            retry(central); return
        }
        peripheral.setNotifyValue(true, for: match)
    }
    func peripheral(_ peripheral: CBPeripheral, didUpdateNotificationStateFor characteristic: CBCharacteristic, error: Error?) {
        if let error = error { print("Subscription failed:", error.localizedDescription); retry(central) }
    }
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard let value = characteristic.value, (value.count == 16 || value.count == 17), value.first == 1 else {
            print("Invalid packet:", error?.localizedDescription ?? "unexpected format")
            retry(central); return
        }
        print("PACKET:" + value.base64EncodedString())
        fflush(stdout)
    }
}
let check = Check()
let central = CBCentralManager(delegate: check, queue: nil)
RunLoop.main.run()
