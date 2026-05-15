import { StatusBar } from "expo-status-bar";
import { useMemo, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Platform,
  RefreshControl,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

const API_URL = Platform.OS === "web" ? "http://localhost:8000/api" : process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000/api";
const DEFAULT_EMAIL = "owner@example.com";
const DEFAULT_PASSWORD = "secret123";

function getRequestErrorMessage(error, path) {
  const message = getErrorMessage(error);
  if (message === "Network request failed") {
    return `Network request failed\nURL: ${API_URL}${path}\nConfirme se o celular acessa o IP do notebook e se a API esta ativa.`;
  }

  return `${message}\nURL: ${API_URL}${path}`;
}

function getErrorMessage(error) {
  if (typeof error === "string") {
    return error;
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  if (error && typeof error === "object") {
    if (typeof error.detail === "string") {
      return error.detail;
    }

    try {
      return JSON.stringify(error);
    } catch {
      return "Unexpected error";
    }
  }

  return "Unexpected error";
}

async function request(path, options = {}) {
  const { headers, ...restOptions } = options;
  const response = await fetch(`${API_URL}${path}`, {
    ...restOptions,
    headers: {
      "Content-Type": "application/json",
      ...(headers || {}),
    },
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Request failed");
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export default function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [busyTaskId, setBusyTaskId] = useState(null);

  const isLoggedIn = useMemo(() => Boolean(token), [token]);

  async function handleLogin(activeEmail = email, activePassword = password) {
    setLoading(true);
    try {
      const payload = await request("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: activeEmail, password: activePassword }),
      });
      setToken(payload.access_token);
      await loadTasks(payload.access_token, false);
    } catch (error) {
      Alert.alert("Falha no login", getRequestErrorMessage(error, "/auth/login"));
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister() {
    setLoading(true);
    try {
      await request("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      await handleLogin(email, password);
      Alert.alert("Conta criada", "Cadastro realizado e login efetuado.");
    } catch (error) {
      Alert.alert("Falha no cadastro", getRequestErrorMessage(error, "/auth/register"));
      setLoading(false);
    }
  }

  async function loadTasks(activeToken = token, showRefreshing = true) {
    if (!activeToken) {
      return;
    }

    if (showRefreshing) {
      setRefreshing(true);
    }

    try {
      const payload = await request("/tasks", {
        headers: {
          Authorization: `Bearer ${activeToken}`,
        },
      });
      setTasks(payload);
    } catch (error) {
      Alert.alert("Falha ao buscar tarefas", getRequestErrorMessage(error, "/tasks"));
    } finally {
      if (showRefreshing) {
        setRefreshing(false);
      }
    }
  }

  async function updateTaskStatus(task) {
    setBusyTaskId(task.id);
    try {
      await request(`/tasks/${task.id}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ is_completed: !task.is_completed }),
      });
      await loadTasks(token, false);
    } catch (error) {
      Alert.alert("Falha ao atualizar status", getRequestErrorMessage(error, `/tasks/${task.id}`));
    } finally {
      setBusyTaskId(null);
    }
  }

  function handleAuthAction() {
    if (authMode === "register") {
      handleRegister();
      return;
    }

    handleLogin();
  }

  function handleLogout() {
    setEmail("");
    setPassword("");
    setToken("");
    setTasks([]);
  }

  function renderTaskItem({ item }) {
    const taskBusy = busyTaskId === item.id;

    return (
      <View style={styles.taskCard}>
        <View style={styles.taskTextWrapper}>
          <Text style={styles.taskTitle}>{item.title}</Text>
          <Text style={styles.taskDescription}>{item.description || "Sem descricao"}</Text>
          <Text style={styles.statusLabel}>{item.is_completed ? "Status: concluida" : "Status: pendente"}</Text>
        </View>
        <TouchableOpacity
          disabled={taskBusy}
          onPress={() => updateTaskStatus(item)}
          style={[styles.secondaryButton, item.is_completed && styles.secondaryButtonDisabled]}
        >
          {taskBusy ? (
            <ActivityIndicator color="#172b1a" />
          ) : (
            <Text style={styles.secondaryButtonText}>{item.is_completed ? "Reabrir" : "Concluir"}</Text>
          )}
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <View
        style={[
          styles.container,
          !isLoggedIn && (Platform.OS === "web" ? styles.loginContainerWeb : styles.loginContainer),
        ]}
      >
        <Text style={styles.title}>Gerenciador de Tarefas</Text>
        {!isLoggedIn ? (
          <View style={[styles.card, styles.loginCard, Platform.OS === "web" && styles.loginCardWeb]}>
            <Text style={[styles.subtitle, styles.loginSubtitle]}>{authMode === "login" ? "Entrar" : "Criar conta"}</Text>
            <Text style={styles.helperText}>
              Teste rapido: {DEFAULT_EMAIL} / {DEFAULT_PASSWORD}
            </Text>
            <Text style={styles.apiInfo}>API atual: {API_URL}</Text>
            <Text style={styles.fieldLabel}>E-mail</Text>
            <TextInput
              autoCapitalize="none"
              keyboardType="email-address"
              onChangeText={setEmail}
              placeholder="E-mail"
              placeholderTextColor="#667085"
              style={styles.input}
              value={email}
            />
            <Text style={styles.fieldLabel}>Senha</Text>
            <TextInput
              onChangeText={setPassword}
              placeholder="Senha"
              placeholderTextColor="#667085"
              secureTextEntry
              style={styles.input}
              value={password}
            />
            <TouchableOpacity disabled={loading} onPress={handleAuthAction} style={styles.button}>
              {loading ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Text style={styles.buttonText}>{authMode === "login" ? "Login" : "Cadastrar e entrar"}</Text>
              )}
            </TouchableOpacity>
            <TouchableOpacity
              disabled={loading}
              onPress={() => setAuthMode(authMode === "login" ? "register" : "login")}
              style={styles.ghostButton}
            >
              <Text style={styles.ghostButtonText}>
                {authMode === "login" ? "Nao tem conta? Cadastre-se" : "Ja tem conta? Fazer login"}
              </Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.card}>
            <View style={styles.headerRow}>
              <Text style={styles.subtitle}>Minhas tarefas</Text>
              <View style={styles.headerActions}>
                <TouchableOpacity onPress={handleLogout}>
                  <Text style={styles.link}>Sair</Text>
                </TouchableOpacity>
              </View>
            </View>
            <Text style={styles.helperText}>O app mobile faz leitura das tarefas e atualizacao do status.</Text>
            <FlatList
              data={tasks}
              keyExtractor={(item) => String(item.id)}
              refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => loadTasks()} />}
              renderItem={renderTaskItem}
              ListEmptyComponent={<Text style={styles.emptyState}>Nenhuma tarefa encontrada.</Text>}
            />
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#f7f4ea",
  },
  container: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 32,
    backgroundColor: "#f7f4ea",
  },
  loginContainer: {
    justifyContent: "center",
    paddingTop: 20,
    paddingBottom: 20,
  },
  loginContainerWeb: {
    alignItems: "center",
    justifyContent: "flex-start",
    paddingTop: 64,
    paddingBottom: 32,
  },
  title: {
    fontSize: 34,
    fontWeight: "800",
    color: "#172b1a",
    marginBottom: 20,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 24,
    fontWeight: "700",
    color: "#172b1a",
    marginBottom: 9,
  },
  card: {
    flex: 1,
    backgroundColor: "#fffdf7",
    borderRadius: 24,
    padding: 20,
    shadowColor: "#6b5f3b",
    shadowOpacity: 0.08,
    shadowRadius: 20,
    shadowOffset: { width: 0, height: 12 },
    elevation: 4,
  },
  loginCard: {
    flex: 0,
    width: "100%",
    maxWidth: 460,
  },
  loginCardWeb: {
    paddingTop: 14,
  },
  loginSubtitle: {
    alignSelf: "center",
    marginTop: -10,
    textAlign: "center",
    width: "100%",
  },
  input: {
    borderWidth: 1,
    borderColor: "#d7d0b8",
    borderRadius: 14,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: "#172b1a",
    backgroundColor: "#ffffff",
    marginBottom: 12,
  },
  fieldLabel: {
    color: "#172b1a",
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 6,
  },
  button: {
    backgroundColor: "#315c38",
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 8,
  },
  buttonText: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "700",
  },
  ghostButton: {
    alignItems: "center",
    marginTop: 14,
  },
  ghostButtonText: {
    color: "#315c38",
    fontSize: 15,
    fontWeight: "600",
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  headerActions: {
    flexDirection: "row",
  },
  helperText: {
    color: "#5b6255",
    marginBottom: 12,
    lineHeight: 20,
  },
  apiInfo: {
    color: "#315c38",
    marginBottom: 12,
    fontSize: 12,
    lineHeight: 18,
  },
  link: {
    color: "#315c38",
    fontWeight: "700",
    marginLeft: 14,
  },
  taskCard: {
    borderWidth: 1,
    borderColor: "#ece4cb",
    borderRadius: 18,
    padding: 16,
    marginBottom: 12,
    backgroundColor: "#fffaf0",
  },
  taskTextWrapper: {
    marginBottom: 14,
  },
  taskTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#172b1a",
  },
  taskDescription: {
    fontSize: 14,
    color: "#5b6255",
    marginTop: 6,
  },
  statusLabel: {
    marginTop: 10,
    color: "#315c38",
    fontWeight: "600",
  },
  secondaryButton: {
    backgroundColor: "#d3e6b0",
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    minWidth: 96,
    alignItems: "center",
  },
  secondaryButtonDisabled: {
    backgroundColor: "#ccd5bf",
  },
  secondaryButtonText: {
    color: "#172b1a",
    fontWeight: "700",
  },
  emptyState: {
    textAlign: "center",
    color: "#667085",
    marginTop: 32,
  },
});
