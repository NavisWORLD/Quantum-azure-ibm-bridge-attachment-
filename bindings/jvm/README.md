# JVM: Java, Kotlin, Scala, Clojure

`QbtClient.java` uses only JDK 17+ APIs (`java.net.http.HttpClient`) and has no external dependencies.

Compile the Java adapter:

```bash
javac -d build bindings/jvm/src/dev/qbt/QbtClient.java bindings/jvm/src/dev/qbt/Smoke.java
java -cp build dev.qbt.Smoke http://127.0.0.1:8766
```

Kotlin can call the same class directly:

```kotlin
import dev.qbt.QbtClient

fun main() {
    val qbt = QbtClient("http://127.0.0.1:8766")
    println(qbt.sample("simulator", 1024, 42))
}
```

Scala and Clojure can use the same JVM class or call the OpenAPI/HTTP contract directly.

For native embedding instead of HTTP, JVM users may bind `qbt.h` through JNI/JNA/Panama according to their deployment requirements.
