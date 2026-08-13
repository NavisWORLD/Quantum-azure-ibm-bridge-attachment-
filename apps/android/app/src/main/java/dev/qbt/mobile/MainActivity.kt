package dev.qbt.mobile

import android.app.Activity
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.text.InputType
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class MainActivity : Activity() {
    private lateinit var endpoint: EditText
    private lateinit var token: EditText
    private lateinit var output: TextView
    private val prefs by lazy { getSharedPreferences("qbt", MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.rgb(8, 17, 29)
        window.navigationBarColor = Color.rgb(8, 17, 29)
        setContentView(buildUi())
    }

    private fun buildUi(): View {
        val scroll = ScrollView(this)
        scroll.setBackgroundColor(Color.rgb(8, 17, 29))
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(22), dp(28), dp(22), dp(28))
        }
        scroll.addView(root)

        root.addView(text("Quantum Bridge Transformer", 28f, true, Color.WHITE))
        root.addView(text("Secure mobile control surface for your own QBT sidecar.", 15f, false, Color.rgb(126, 170, 220)).apply {
            setPadding(0, dp(6), 0, dp(22))
        })

        val card = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(18), dp(18), dp(18))
            background = rounded(Color.rgb(16, 30, 48), 18f)
        }
        root.addView(card, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT))

        card.addView(label("Sidecar URL"))
        endpoint = field(prefs.getString("endpoint", "http://192.168.1.2:8766") ?: "")
        card.addView(endpoint)
        card.addView(label("Bearer token").apply { setPadding(0, dp(14), 0, dp(6)) })
        token = field(prefs.getString("token", "") ?: "", secret = true)
        card.addView(token)

        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(0, dp(18), 0, 0)
        }
        row.addView(actionButton("Health") { call("GET", "/health", null) }, weightParams())
        row.addView(actionButton("Sample") {
            call("POST", "/v1/sample", JSONObject().put("provider", "simulator").put("shots", 1024).put("seed", 42))
        }, weightParams(left = 8))
        card.addView(row)

        val save = actionButton("Save connection") {
            prefs.edit().putString("endpoint", endpoint.text.toString().trim()).putString("token", token.text.toString()).apply()
            showResult(JSONObject().put("saved", true).put("note", "Stored only in this app's private preferences."))
        }
        card.addView(save, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(48)).apply { topMargin = dp(10) })

        root.addView(text("Result", 17f, true, Color.WHITE).apply { setPadding(0, dp(22), 0, dp(8)) })
        output = TextView(this).apply {
            text = "Connect to a QBT sidecar, then run Health or Sample."
            setTextColor(Color.rgb(221, 241, 255))
            textSize = 13f
            typeface = Typeface.MONOSPACE
            setPadding(dp(16), dp(16), dp(16), dp(16))
            setTextIsSelectable(true)
            background = rounded(Color.rgb(5, 13, 23), 16f)
        }
        root.addView(output, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(260)))

        root.addView(text(
            "BYOK: this app contains no IBM or Azure credentials. For LAN access, start qbt serve on a reachable host and require QBT_SIDECAR_TOKEN. Prefer HTTPS outside a trusted local network.",
            12f, false, Color.rgb(126, 170, 220)
        ).apply { setPadding(0, dp(18), 0, 0) })
        return scroll
    }

    private fun call(method: String, path: String, body: JSONObject?) {
        val base = endpoint.text.toString().trim().trimEnd('/')
        val bearer = token.text.toString()
        output.text = "Working…"
        thread {
            try {
                val connection = URL(base + path).openConnection() as HttpURLConnection
                connection.requestMethod = method
                connection.connectTimeout = 10_000
                connection.readTimeout = 20_000
                connection.setRequestProperty("Accept", "application/json")
                if (bearer.isNotBlank()) connection.setRequestProperty("Authorization", "Bearer $bearer")
                if (body != null) {
                    connection.doOutput = true
                    connection.setRequestProperty("Content-Type", "application/json")
                    connection.outputStream.use { it.write(body.toString().toByteArray()) }
                }
                val code = connection.responseCode
                val stream = if (code in 200..299) connection.inputStream else connection.errorStream
                val raw = stream?.bufferedReader()?.use { it.readText() } ?: ""
                val result = try { JSONObject(raw) } catch (_: Exception) { JSONObject().put("status", code).put("body", raw) }
                runOnUiThread { showResult(result) }
            } catch (exc: Exception) {
                runOnUiThread { showResult(JSONObject().put("error", exc.message ?: exc.javaClass.simpleName)) }
            }
        }
    }

    private fun showResult(obj: JSONObject) {
        output.text = obj.toString(2)
    }

    private fun label(value: String) = text(value, 13f, true, Color.rgb(220, 236, 255)).apply { setPadding(0, 0, 0, dp(6)) }

    private fun field(value: String, secret: Boolean = false) = EditText(this).apply {
        setText(value)
        setTextColor(Color.WHITE)
        setHintTextColor(Color.GRAY)
        textSize = 14f
        setPadding(dp(12), 0, dp(12), 0)
        background = rounded(Color.rgb(19, 38, 61), 12f)
        inputType = if (secret) InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD else InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI
        layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(48))
    }

    private fun actionButton(label: String, onClick: () -> Unit) = Button(this).apply {
        text = label
        isAllCaps = false
        setTextColor(Color.WHITE)
        textSize = 14f
        background = rounded(Color.rgb(41, 97, 164), 14f)
        setOnClickListener { onClick() }
    }

    private fun text(value: String, size: Float, bold: Boolean, color: Int) = TextView(this).apply {
        text = value
        textSize = size
        setTextColor(color)
        if (bold) setTypeface(typeface, Typeface.BOLD)
    }

    private fun rounded(color: Int, radiusDp: Float) = GradientDrawable().apply {
        shape = GradientDrawable.RECTANGLE
        setColor(color)
        cornerRadius = dp(radiusDp.toInt()).toFloat()
    }

    private fun weightParams(left: Int = 0) = LinearLayout.LayoutParams(0, dp(48), 1f).apply { leftMargin = dp(left) }
    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()
}
